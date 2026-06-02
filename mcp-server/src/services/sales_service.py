from sqlalchemy.orm import Session
from src.repositories.orders_repository import OrdersRepository
from src.repositories.products_repository import ProductsRepository
from src.services.period_service import PeriodService
from src.services.analytics_service import calculate_variation
from src.business_rules.revenue_rules import REVENUE_VALID_STATUSES, CANCELLATION_STATUS, PENDING_STATUS
from src.models.responses import (
    GMVResponse, GMVComparisonResponse, AverageTicketResponse, 
    AverageTicketYoYResponse, TopProductsResponse, 
    CancellationAnalysisResponse, BusinessOverviewResponse, StockHealthResponse
)
from typing import Dict, Any, List

class SalesService:
    def __init__(self, db: Session):
        self.orders_repo = OrdersRepository(db)
        self.products_repo = ProductsRepository(db)
        self.period_service = PeriodService()

    def get_gmv(self, period_str: str) -> Dict[str, Any]:
        start, end, label = self.period_service.resolve_period(period_str)
        value = self.orders_repo.get_gmv(start, end)
        
        response = GMVResponse(
            period={
                "label": label,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            },
            value=round(value, 2),
            included_statuses=REVENUE_VALID_STATUSES,
            excluded_statuses=[PENDING_STATUS, CANCELLATION_STATUS]
        )
        return response.model_dump()

    def get_gmv_comparison(self, current_period: str, comparison_period: str = None) -> Dict[str, Any]:
        start, end, label = self.period_service.resolve_period(current_period)
        current_value = self.orders_repo.get_gmv(start, end)
        
        if comparison_period:
            comp_start, comp_end, comp_label = self.period_service.resolve_period(comparison_period)
        else:
            comp_start, comp_end, comp_label = self.period_service.get_comparison_period(current_period, start, end)
            
        previous_value = self.orders_repo.get_gmv(comp_start, comp_end)
        
        variation = calculate_variation(current_value, previous_value)
        
        response = GMVComparisonResponse(
            current={
                "label": label,
                "value": round(current_value, 2),
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            },
            comparison={
                "label": comp_label,
                "value": round(previous_value, 2),
                "start_date": comp_start.strftime("%Y-%m-%d"),
                "end_date": comp_end.strftime("%Y-%m-%d")
            },
            **variation
        )
        return response.model_dump()

    def get_average_ticket(self, period_str: str) -> Dict[str, Any]:
        start, end, label = self.period_service.resolve_period(period_str)
        value = self.orders_repo.get_average_ticket(start, end)
        
        response = AverageTicketResponse(
            period={
                "label": label,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            },
            value=round(value, 2)
        )
        return response.model_dump()

    def get_average_ticket_yoy(self) -> Dict[str, Any]:
        start_curr, end_curr, _ = self.period_service.resolve_period("current_year")
        current_value = self.orders_repo.get_average_ticket(start_curr, end_curr)
        
        start_prev = start_curr.replace(year=start_curr.year - 1)
        prev_year_limit = start_prev.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=0)
        candidate_end_prev = start_prev + (end_curr - start_curr)
        end_prev = candidate_end_prev if candidate_end_prev <= prev_year_limit else prev_year_limit
        previous_value = self.orders_repo.get_average_ticket(start_prev, end_prev)
        
        variation = calculate_variation(current_value, previous_value)
        
        response = AverageTicketYoYResponse(
            current_year={
                "label": "current_year_to_date",
                "value": round(current_value, 2),
                "start_date": start_curr.strftime("%Y-%m-%d"),
                "end_date": end_curr.strftime("%Y-%m-%d")
            },
            previous_year={
                "label": "previous_year_to_date",
                "value": round(previous_value, 2),
                "start_date": start_prev.strftime("%Y-%m-%d"),
                "end_date": end_prev.strftime("%Y-%m-%d")
            },
            **variation
        )
        return response.model_dump()

    def get_top_products(self, period_str: str, limit: int = 5) -> Dict[str, Any]:
        start, end, label = self.period_service.resolve_period(period_str)
        items = self.products_repo.get_top_products(start, end, limit)
        
        response = TopProductsResponse(
            period={
                "label": label,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            },
            items=[
                {**item, "revenue": round(item["revenue"], 2)} 
                for item in items
            ]
        )
        return response.model_dump()

    def get_cancellation_analysis(self, period_str: str, limit: int = 3) -> Dict[str, Any]:
        start, end, label = self.period_service.resolve_period(period_str)
        
        metrics = self.orders_repo.get_cancelled_metrics(start, end)
        top_categories = self.orders_repo.get_top_categories_by_cancellation(start, end, limit)
        top_products = self.products_repo.get_top_cancelled_products(start, end, limit)
        categories_by_rate = self.orders_repo.get_category_cancellation_rates(start, end, limit)
        categories_with_top_products = []
        for category_row in categories_by_rate:
            category_name = category_row["category"]
            responsible_products = self.products_repo.get_top_cancelled_products_by_category(
                start, end, category_name, limit
            )
            categories_with_top_products.append({
                "category": category_name,
                "cancelled_orders": int(category_row["cancelled_orders"]),
                "total_orders": int(category_row["total_orders"]),
                "cancellation_rate_percentage": float(category_row["cancellation_rate_percentage"]),
                "cancelled_items": int(category_row["cancelled_items"]),
                "total_items": int(category_row["total_items"]),
                "cancelled_revenue": round(float(category_row["cancelled_revenue"]), 2),
                "top_products": [
                    {
                        "product_id": int(p["product_id"]),
                        "product_name": p["product_name"],
                        "category": p["category"],
                        "cancelled_orders": int(p["cancelled_orders"]),
                        "cancelled_items": int(p["cancelled_items"]),
                        "cancelled_revenue": round(float(p["cancelled_revenue"]), 2),
                    }
                    for p in responsible_products
                ],
            })
        
        response = CancellationAnalysisResponse(
            period={
                "label": label,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            },
            total_cancelled_orders=metrics["total_cancelled_orders"],
            total_cancelled_revenue=round(metrics["cancelled_revenue"], 2),
            top_categories=[
                {**cat, "cancelled_revenue": round(cat["cancelled_revenue"], 2)}
                for cat in top_categories
            ],
            top_products=[
                {**prod, "cancelled_revenue": round(prod["cancelled_revenue"], 2)}
                for prod in top_products
            ],
            categories_by_cancellation_rate=categories_with_top_products
        )
        return response.model_dump()

    def get_business_overview(self, period_str: str) -> Dict[str, Any]:
        start, end, label = self.period_service.resolve_period(period_str)
        
        gmv = self.orders_repo.get_gmv(start, end)
        avg_ticket = self.orders_repo.get_average_ticket(start, end)
        valid_orders = self.orders_repo.get_valid_orders_count(start, end)
        cancelled_orders = self.orders_repo.get_orders_count(start, end, status=CANCELLATION_STATUS)
        
        total_orders = valid_orders + cancelled_orders
        cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
        
        top_categories = self.orders_repo.get_top_categories_by_cancellation(start, end, limit=3)
        
        response = BusinessOverviewResponse(
            period={
                "label": label,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d")
            },
            gmv=round(gmv, 2),
            average_ticket=round(avg_ticket, 2),
            valid_orders=int(valid_orders),
            cancelled_orders=int(cancelled_orders),
            cancellation_rate_percentage=round(cancellation_rate, 2),
            top_categories=[
                {"category": c["category"], "cancelled_orders": c["cancelled_orders"]}
                for c in top_categories
            ]
        )
        return response.model_dump()

    def get_stock_health(self, low_stock_threshold: int = 10, limit: int = 10) -> Dict[str, Any]:
        stock_column = self.products_repo.detect_stock_column()
        if not stock_column:
            response = StockHealthResponse(
                supported=False,
                message="No stock/inventory column found on products table",
                stock_column="unavailable",
                total_products=0,
                out_of_stock_products=0,
                low_stock_products=0,
                low_stock_threshold=int(low_stock_threshold),
                items=[],
            )
            return response.model_dump()

        data = self.products_repo.get_stock_health(stock_column, int(low_stock_threshold), int(limit))
        response = StockHealthResponse(
            stock_column=data["stock_column"],
            total_products=data["total_products"],
            out_of_stock_products=data["out_of_stock_products"],
            low_stock_products=data["low_stock_products"],
            low_stock_threshold=int(low_stock_threshold),
            items=[
                {
                    "product_id": int(item["product_id"]),
                    "product_name": item["product_name"],
                    "category": item["category"],
                    "stock_quantity": int(item["stock_quantity"]),
                }
                for item in data["items"]
            ],
        )
        return response.model_dump()
