REVENUE_VALID_STATUSES = ["processing", "shipped", "delivered"]
CANCELLATION_STATUS = "cancelled"
PENDING_STATUS = "pending"

def is_revenue_valid(status: str) -> bool:
    """Verifica se um status de pedido é válido para métricas de receita."""
    return status in REVENUE_VALID_STATUSES
