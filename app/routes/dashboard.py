from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.access_control import require_role
from app.schemas.dashboard import DashboardSummary, TrendResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])



@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get financial dashboard summary",
    description="Returns aggregated financial summary. Includes total income, total expense, net balance, record count, and category breakdown. Available to **all roles**."
)
async def get_summary(
    start_date: date | None = Query(
        default=None, description="Start date for summary"
    ),
    end_date: date | None = Query(
        default=None, description="End date for summary"
    ),
    _current_user: dict = Depends(require_role(["viewer", "analyst", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> DashboardSummary:
    return await dashboard_service.get_summary(
        db, start_date=start_date, end_date=end_date
    )


@router.get(
    "/trends",
    response_model=TrendResponse,
    summary="Get financial trends over time",
    description="Returns income vs expense trends grouped by period. Requires **analyst** or **admin** role."
)
async def get_trends(
    period: str = Query(
        default="monthly",
        pattern="^(monthly|daily)$",
        description="Trend period: 'monthly' or 'daily'",
    ),
    _current_user: dict = Depends(require_role(["analyst", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> TrendResponse:
    return await dashboard_service.get_trends(db, period)
