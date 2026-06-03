from src.database.connection import SessionLocal
from src.services.sales_service import SalesService
from src.services.cache_service import mcp_cache

def register_analytics_tools(mcp, tool_telemetry):
    @mcp.tool()
    @tool_telemetry
    @mcp_cache(ttl=300)
    def get_top_products(period: str, limit: int = 5) -> dict:
        """
        Returns the top selling products for a given period.
        """
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_top_products(period, limit)

    @mcp.tool()
    @tool_telemetry
    @mcp_cache(ttl=300)
    def get_cancellation_analysis(period: str, limit: int = 3) -> dict:
        """
        Analyzes cancelled orders, including top categories and products with highest cancellation rates.
        """
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_cancellation_analysis(period, limit)

    @mcp.tool()
    @tool_telemetry
    @mcp_cache(ttl=300)
    def get_business_overview(period: str) -> dict:
        """
        Returns a high-level executive summary of the business for a given period.
        """
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_business_overview(period)

    @mcp.tool()
    @tool_telemetry
    @mcp_cache(ttl=300)
    def get_stock_health(low_stock_threshold: int = 10, limit: int = 10) -> dict:
        """
        Returns stock health metrics if the database contains stock/inventory data on products table.
        """
        if limit <= 0:
            raise ValueError("Limit must be greater than zero")
        if low_stock_threshold < 0:
            raise ValueError("low_stock_threshold must be >= 0")
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_stock_health(low_stock_threshold=low_stock_threshold, limit=limit)
