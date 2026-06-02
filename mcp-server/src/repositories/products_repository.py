from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.business_rules.revenue_rules import REVENUE_VALID_STATUSES, CANCELLATION_STATUS

class ProductsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_top_products(self, start_date: datetime, end_date: datetime, limit: int = 5) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                p.id as product_id,
                p.name as product_name,
                p.category,
                SUM(oi.quantity) as quantity_sold,
                SUM(oi.unit_price * oi.quantity) as revenue
            FROM order_item oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.created_at >= :start AND o.created_at <= :end
            AND o.status IN :statuses
            GROUP BY p.id, p.name, p.category
            ORDER BY revenue DESC
            LIMIT :limit
        """).bindparams(bindparam("statuses", expanding=True))

        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "statuses": list(REVENUE_VALID_STATUSES),
            "limit": limit
        }).mappings().all()
        return [dict(row) for row in result]

    def get_top_cancelled_products(self, start_date: datetime, end_date: datetime, limit: int = 3) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                p.id as product_id,
                p.name as product_name,
                p.category,
                SUM(oi.quantity) as cancelled_items,
                SUM(oi.unit_price * oi.quantity) as cancelled_revenue
            FROM order_item oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.created_at >= :start AND o.created_at <= :end
            AND o.status = :status
            GROUP BY p.id, p.name, p.category
            ORDER BY cancelled_items DESC
            LIMIT :limit
        """)
        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "status": CANCELLATION_STATUS,
            "limit": limit
        }).mappings().all()
        return [dict(row) for row in result]

    def get_top_cancelled_products_by_category(self, start_date: datetime, end_date: datetime, category: str, limit: int = 3) -> List[Dict[str, Any]]:
        query = text("""
            SELECT
                p.id as product_id,
                p.name as product_name,
                p.category,
                COUNT(DISTINCT o.id) as cancelled_orders,
                SUM(oi.quantity) as cancelled_items,
                SUM(oi.unit_price * oi.quantity) as cancelled_revenue
            FROM order_item oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.created_at >= :start AND o.created_at <= :end
            AND o.status = :status
            AND p.category = :category
            GROUP BY p.id, p.name, p.category
            ORDER BY cancelled_orders DESC, cancelled_revenue DESC, cancelled_items DESC
            LIMIT :limit
        """)
        result = self.db.execute(query, {
            "start": start_date,
            "end": end_date,
            "status": CANCELLATION_STATUS,
            "category": category,
            "limit": limit,
        }).mappings().all()
        return [dict(row) for row in result]

    def detect_stock_column(self) -> Optional[str]:
        candidates = [
            "stock_quantity",
            "quantity_in_stock",
            "qty_in_stock",
            "inventory_quantity",
            "stock",
        ]

        query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'products'
              AND column_name IN :candidates
        """).bindparams(bindparam("candidates", expanding=True))

        result = self.db.execute(query, {"candidates": candidates}).scalars().all()
        if not result:
            return None

        result_set = set(result)
        for name in candidates:
            if name in result_set:
                return name
        return result[0]

    def get_stock_health(self, stock_column: str, low_stock_threshold: int, limit: int) -> Dict[str, Any]:
        if low_stock_threshold < 0:
            raise ValueError("low_stock_threshold must be >= 0")

        metrics_query = text(f"""
            SELECT
                COUNT(*) as total_products,
                COUNT(*) FILTER (WHERE p.{stock_column} <= 0) as out_of_stock_products,
                COUNT(*) FILTER (WHERE p.{stock_column} > 0 AND p.{stock_column} <= :threshold) as low_stock_products
            FROM products p
        """)
        metrics = self.db.execute(metrics_query, {"threshold": low_stock_threshold}).mappings().first()

        items_query = text(f"""
            SELECT
                p.id as product_id,
                p.name as product_name,
                p.category,
                p.{stock_column} as stock_quantity
            FROM products p
            WHERE p.{stock_column} > 0 AND p.{stock_column} <= :threshold
            ORDER BY p.{stock_column} ASC, p.id ASC
            LIMIT :limit
        """)
        items = self.db.execute(items_query, {"threshold": low_stock_threshold, "limit": limit}).mappings().all()

        return {
            "stock_column": stock_column,
            "total_products": int(metrics["total_products"]),
            "out_of_stock_products": int(metrics["out_of_stock_products"]),
            "low_stock_products": int(metrics["low_stock_products"]),
            "items": [dict(row) for row in items],
        }
