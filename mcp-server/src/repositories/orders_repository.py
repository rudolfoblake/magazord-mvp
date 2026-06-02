from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.business_rules.revenue_rules import REVENUE_VALID_STATUSES, CANCELLATION_STATUS

class OrdersRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_gmv(self, start_date: datetime, end_date: datetime) -> float:
        query = text("""
            SELECT COALESCE(SUM(total_value), 0)
            FROM orders
            WHERE created_at >= :start AND created_at <= :end
            AND status IN :statuses
        """).bindparams(bindparam("statuses", expanding=True))

        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "statuses": list(REVENUE_VALID_STATUSES)
        }).scalar()
        return float(result)

    def get_average_ticket(self, start_date: datetime, end_date: datetime) -> float:
        query = text("""
            SELECT COALESCE(AVG(total_value), 0)
            FROM orders
            WHERE created_at >= :start AND created_at <= :end
            AND status IN :statuses
        """).bindparams(bindparam("statuses", expanding=True))

        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "statuses": list(REVENUE_VALID_STATUSES)
        }).scalar()
        return float(result)

    def get_orders_count(self, start_date: datetime, end_date: datetime, status: Optional[str] = None) -> int:
        sql = "SELECT COUNT(*) FROM orders WHERE created_at >= :start AND created_at <= :end"
        params = {"start": start_date, "end": end_date}
        
        if status:
            sql += " AND status = :status"
            params["status"] = status

        result = self.db.execute(text(sql), params).scalar()
        return int(result)

    def get_valid_orders_count(self, start_date: datetime, end_date: datetime) -> int:
        query = text("""
            SELECT COUNT(*) FROM orders 
            WHERE created_at >= :start AND created_at <= :end 
            AND status IN :statuses
        """).bindparams(bindparam("statuses", expanding=True))

        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "statuses": list(REVENUE_VALID_STATUSES)
        }).scalar()
        return int(result)

    def get_cancelled_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        query = text("""
            SELECT 
                COUNT(*) as total_cancelled_orders,
                COALESCE(SUM(total_value), 0) as cancelled_revenue
            FROM orders
            WHERE created_at >= :start AND created_at <= :end
            AND status = :status
        """)
        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "status": CANCELLATION_STATUS
        }).mappings().first()
        return dict(result)

    def get_top_categories_by_cancellation(self, start_date: datetime, end_date: datetime, limit: int = 3) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                p.category,
                COUNT(DISTINCT o.id) as cancelled_orders,
                COUNT(oi.id) as cancelled_items,
                SUM(oi.unit_price * oi.quantity) as cancelled_revenue
            FROM orders o
            JOIN order_item oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.created_at >= :start AND o.created_at <= :end
            AND o.status = :status
            GROUP BY p.category
            ORDER BY cancelled_orders DESC
            LIMIT :limit
        """)
        result = self.db.execute(query, {
            "start": start_date, 
            "end": end_date, 
            "status": CANCELLATION_STATUS,
            "limit": limit
        }).mappings().all()
        return [dict(row) for row in result]

    def get_category_cancellation_rates(self, start_date: datetime, end_date: datetime, limit: int = 3) -> List[Dict[str, Any]]:
        statuses = list(REVENUE_VALID_STATUSES) + [CANCELLATION_STATUS]

        query = text("""
            SELECT
                p.category,
                COUNT(DISTINCT o.id) FILTER (WHERE o.status = :cancel_status) as cancelled_orders,
                COUNT(DISTINCT o.id) as total_orders,
                CASE
                    WHEN COUNT(DISTINCT o.id) = 0 THEN 0
                    ELSE ROUND((COUNT(DISTINCT o.id) FILTER (WHERE o.status = :cancel_status)) * 100.0 / COUNT(DISTINCT o.id), 2)
                END as cancellation_rate_percentage,
                COUNT(oi.id) FILTER (WHERE o.status = :cancel_status) as cancelled_items,
                COUNT(oi.id) as total_items,
                COALESCE(SUM(oi.unit_price * oi.quantity) FILTER (WHERE o.status = :cancel_status), 0) as cancelled_revenue
            FROM orders o
            JOIN order_item oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.created_at >= :start AND o.created_at <= :end
            AND o.status IN :statuses
            GROUP BY p.category
            ORDER BY cancellation_rate_percentage DESC, cancelled_orders DESC, cancelled_revenue DESC
            LIMIT :limit
        """).bindparams(bindparam("statuses", expanding=True))

        result = self.db.execute(query, {
            "start": start_date,
            "end": end_date,
            "statuses": statuses,
            "cancel_status": CANCELLATION_STATUS,
            "limit": limit,
        }).mappings().all()
        return [dict(row) for row in result]
