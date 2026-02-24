import datetime as dt

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_fleet_manager
from app.database import get_db
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/tco")
async def tco_report(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ReportService(db)
    return await svc.tco_report(start_date, end_date)


@router.get("/fleet-utilization")
async def fleet_utilization(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ReportService(db)
    return await svc.fleet_utilization()


@router.get("/fuel-consumption")
async def fuel_consumption(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ReportService(db)
    return await svc.fuel_consumption(start_date, end_date)


@router.get("/expense-analysis")
async def expense_analysis(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ReportService(db)
    return await svc.expense_analysis(start_date, end_date)


@router.get("/maintenance-history")
async def maintenance_history(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ReportService(db)
    return await svc.maintenance_history(start_date, end_date)


# --- Export endpoints ---

@router.get("/export/tco.xlsx")
async def export_tco_excel(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_fleet_manager),
):
    svc = ReportService(db)
    data = await svc.export_tco_excel(start_date, end_date)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tco_report.xlsx"},
    )


@router.get("/export/fuel.xlsx")
async def export_fuel_excel(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_fleet_manager),
):
    svc = ReportService(db)
    data = await svc.export_fuel_excel(start_date, end_date)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=fuel_consumption.xlsx"},
    )


@router.get("/export/maintenance.xlsx")
async def export_maintenance_excel(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_fleet_manager),
):
    svc = ReportService(db)
    data = await svc.export_maintenance_excel(start_date, end_date)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=maintenance_history.xlsx"},
    )


@router.get("/export/expenses.csv")
async def export_expenses_csv(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_fleet_manager),
):
    svc = ReportService(db)
    data = await svc.export_expense_csv(start_date, end_date)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expense_analysis.csv"},
    )
