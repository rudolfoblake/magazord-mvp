from src.database.connection import SessionLocal
from src.services.sales_service import SalesService
from src.services.cache_service import mcp_cache

def register_sales_tools(mcp, tool_telemetry):
    @mcp.tool()
    @mcp_cache(ttl=300)
    @tool_telemetry
    def get_gmv(period: str) -> dict:
        """
        Returns the Gross Merchandise Volume (GMV) for a given period.
        Supported periods: today, yesterday, current_month, last_month, current_quarter, last_quarter, current_year, last_year, last_12_months.
        """
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_gmv(period)

    @mcp.tool()
    @mcp_cache(ttl=300)
    @tool_telemetry
    def get_gmv_comparison(current_period: str, comparison_period: str = None) -> dict:
        """
        Compares the GMV of the current period with a comparison period.
        If comparison_period is not provided, it automatically chooses the previous equivalent period.
        """
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_gmv_comparison(current_period, comparison_period)

    @mcp.tool()
    @mcp_cache(ttl=300)
    @tool_telemetry
    def get_average_ticket(period: str) -> dict:
        """
        Returns the average ticket value for a given period.
        """
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_average_ticket(period)

    @mcp.tool()
    @mcp_cache(ttl=300)
    @tool_telemetry
    def get_average_ticket_yoy() -> dict:
        """
        Compares the average ticket value of the current year with the previous year (Year-over-Year).
        """
        with SessionLocal() as db:
            service = SalesService(db)
            return service.get_average_ticket_yoy()
