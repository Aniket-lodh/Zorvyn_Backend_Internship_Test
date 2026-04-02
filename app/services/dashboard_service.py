from datetime import date
from sqlalchemy import String, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord, RecordType
from app.schemas.dashboard import (
    CategoryBreakdown,
    DashboardSummary,
    TrendItem,
    TrendResponse,
)


async def get_summary(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DashboardSummary:
    """Returns total income, total expense, net balance, record count and a breakdown of totals by category."""
    stmt = select(
        func.count(FinancialRecord.id).label("record_count"),
        func.coalesce( # To prevent any null check scenarios when queried on empty database.
            func.sum(
                case(
                    (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                    else_=0,
                )
            ),
            0,
        ).label("total_income"),
        func.coalesce( # To prevent any null check scenarios when queried on empty database.
            func.sum(
                case(
                    (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                    else_=0,
                )
            ),
            0,
        ).label("total_expense"),
    ).select_from(FinancialRecord)

    if start_date is not None:
        stmt = stmt.where(FinancialRecord.date >= start_date)
    if end_date is not None:
        stmt = stmt.where(FinancialRecord.date <= end_date)

    result = await db.execute(stmt)
    row = result.one()
    total_income = float(row.total_income)
    total_expense = float(row.total_expense)

    cat_stmt = (
        select(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .select_from(FinancialRecord)
    )

    if start_date is not None:
        cat_stmt = cat_stmt.where(FinancialRecord.date >= start_date)
    if end_date is not None:
        cat_stmt = cat_stmt.where(FinancialRecord.date <= end_date)

    cat_stmt = cat_stmt.group_by(FinancialRecord.category).order_by(
        func.sum(FinancialRecord.amount).desc()
    )

    cat_result = await db.execute(cat_stmt)
    category_breakdown = [
        CategoryBreakdown(category=r.category, total=float(r.total))
        for r in cat_result.all()
    ]

    return DashboardSummary(
        total_income=total_income,
        total_expense=total_expense,
        net_balance=total_income - total_expense,
        record_count=row.record_count,
        category_breakdown=category_breakdown,
    )


async def get_trends(db: AsyncSession, period: str = "monthly") -> TrendResponse:
    """Returns time-based income vs expense trends. period arg can be monthly or daily."""

    if period not in ["daily", "monthly"]:
        raise ValueError("Period must be either 'daily' or 'monthly'")

    if period == "daily":
        period_expr = cast(FinancialRecord.date, String)
    else:
        period_expr = func.to_char(FinancialRecord.date, "YYYY-MM")

    stmt = (
        select(
            period_expr.label("period"),
            func.coalesce(
                func.sum(
                    case(
                        (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("income"),
            func.coalesce(
                func.sum(
                    case(
                        (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("expense"),
        )
        .select_from(FinancialRecord)
        .group_by(period_expr)
        .order_by(period_expr)
    )

    result = await db.execute(stmt)
    trends = [
        TrendItem(
            period=r.period,
            income=float(r.income),
            expense=float(r.expense),
            net=float(r.income) - float(r.expense),
        )
        for r in result.all()
    ]

    return TrendResponse(trends=trends)
