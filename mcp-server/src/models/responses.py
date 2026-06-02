from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PeriodInfo(BaseModel):
    label: str
    start_date: str
    end_date: str

class GMVResponse(BaseModel):
    metric: str = "gmv"
    period: PeriodInfo
    value: float
    currency: str = "BRL"
    included_statuses: List[str]
    excluded_statuses: List[str]

class GMVComparisonItem(BaseModel):
    label: str
    value: float
    start_date: str
    end_date: str

class GMVComparisonResponse(BaseModel):
    metric: str = "gmv_comparison"
    current: GMVComparisonItem
    comparison: GMVComparisonItem
    variation_percentage: Optional[float]
    direction: str
    message: Optional[str] = None

class AverageTicketResponse(BaseModel):
    metric: str = "average_ticket"
    period: PeriodInfo
    value: float
    currency: str = "BRL"

class AverageTicketYoYResponse(BaseModel):
    metric: str = "average_ticket_yoy"
    current_year: GMVComparisonItem
    previous_year: GMVComparisonItem
    variation_percentage: Optional[float]
    direction: str
    message: Optional[str] = None

class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity_sold: int
    revenue: float

class TopProductsResponse(BaseModel):
    metric: str = "top_products"
    period: PeriodInfo
    items: List[TopProductItem]

class CancellationCategoryItem(BaseModel):
    category: str
    cancelled_orders: int
    cancelled_items: int
    cancelled_revenue: float

class CancellationProductItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    cancelled_items: int
    cancelled_revenue: float

class CancellationResponsibleProductItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    cancelled_orders: int
    cancelled_items: int
    cancelled_revenue: float

class CancellationCategoryRateItem(BaseModel):
    category: str
    cancelled_orders: int
    total_orders: int
    cancellation_rate_percentage: float
    cancelled_items: int
    total_items: int
    cancelled_revenue: float
    top_products: List[CancellationResponsibleProductItem]

class CancellationAnalysisResponse(BaseModel):
    metric: str = "cancellation_analysis"
    period: PeriodInfo
    total_cancelled_orders: int
    total_cancelled_revenue: float
    top_categories: List[CancellationCategoryItem]
    top_products: List[CancellationProductItem]
    categories_by_cancellation_rate: List[CancellationCategoryRateItem]

class BusinessOverviewResponse(BaseModel):
    metric: str = "business_overview"
    period: PeriodInfo
    gmv: float
    average_ticket: float
    valid_orders: int
    cancelled_orders: int
    cancellation_rate_percentage: float
    top_categories: List[Dict[str, Any]]

class StockHealthItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    stock_quantity: int

class StockHealthResponse(BaseModel):
    metric: str = "stock_health"
    supported: bool = True
    message: Optional[str] = None
    stock_column: str
    total_products: int
    out_of_stock_products: int
    low_stock_products: int
    low_stock_threshold: int
    items: List[StockHealthItem]
