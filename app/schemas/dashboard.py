from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category: str
    total: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    record_count: int
    category_breakdown: list[CategoryBreakdown]


class TrendItem(BaseModel):
    period: str
    income: float
    expense: float
    net: float


class TrendResponse(BaseModel):
    trends: list[TrendItem]
