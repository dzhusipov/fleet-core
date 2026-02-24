import datetime as dt

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.report_service import ReportService
from app.web.deps import get_web_user

router = APIRouter(prefix="/reports", tags=["web-reports"])


@router.get("", response_class=HTMLResponse)
async def reports_index(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return request.app.state.templates.TemplateResponse(
        "reports/index.html",
        {
            "request": request,
            "user": user,
            "active_page": "reports",
            **request.app.state.template_globals(request),
        },
    )


@router.get("/tco", response_class=HTMLResponse)
async def report_tco(
    request: Request,
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    svc = ReportService(db)
    data = await svc.tco_report(start_date, end_date)
    return request.app.state.templates.TemplateResponse(
        "reports/tco.html",
        {
            "request": request,
            "user": user,
            "active_page": "reports",
            "data": data,
            "start_date": start_date,
            "end_date": end_date,
            **request.app.state.template_globals(request),
        },
    )


@router.get("/fuel", response_class=HTMLResponse)
async def report_fuel(
    request: Request,
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    svc = ReportService(db)
    data = await svc.fuel_consumption(start_date, end_date)
    return request.app.state.templates.TemplateResponse(
        "reports/fuel.html",
        {
            "request": request,
            "user": user,
            "active_page": "reports",
            "data": data,
            "start_date": start_date,
            "end_date": end_date,
            **request.app.state.template_globals(request),
        },
    )


@router.get("/expenses", response_class=HTMLResponse)
async def report_expenses(
    request: Request,
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    db: AsyncSession = Depends(get_db),
):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    svc = ReportService(db)
    data = await svc.expense_analysis(start_date, end_date)
    return request.app.state.templates.TemplateResponse(
        "reports/expenses.html",
        {
            "request": request,
            "user": user,
            "active_page": "reports",
            "data": data,
            "start_date": start_date,
            "end_date": end_date,
            **request.app.state.template_globals(request),
        },
    )


# Excel/CSV exports from web UI

@router.get("/export/tco.xlsx")
async def web_export_tco(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    svc = ReportService(db)
    content = await svc.export_tco_excel(start_date, end_date)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tco_report.xlsx"},
    )


@router.get("/export/fuel.xlsx")
async def web_export_fuel(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    svc = ReportService(db)
    content = await svc.export_fuel_excel(start_date, end_date)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=fuel_consumption.xlsx"},
    )


@router.get("/export/expenses.csv")
async def web_export_expenses(
    start_date: dt.date | None = None,
    end_date: dt.date | None = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    svc = ReportService(db)
    content = await svc.export_expense_csv(start_date, end_date)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expense_analysis.csv"},
    )
