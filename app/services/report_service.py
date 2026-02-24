"""Report service for generating fleet analytics and exportable data."""

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract, ContractStatus
from app.models.expense import Expense, ExpenseCategory
from app.models.maintenance import MaintenanceRecord
from app.models.vehicle import Vehicle, VehicleStatus
from app.utils.export import CSVExporter, ExcelExporter


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def tco_report(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> list[dict]:
        """Total Cost of Ownership per vehicle."""
        query = (
            select(
                Vehicle.id,
                Vehicle.license_plate,
                Vehicle.brand,
                Vehicle.model,
                Vehicle.year,
                Vehicle.purchase_price,
                func.coalesce(func.sum(Expense.amount), 0).label("total_expenses"),
            )
            .outerjoin(Expense, Expense.vehicle_id == Vehicle.id)
        )
        if start_date:
            query = query.where(Expense.date >= start_date)
        if end_date:
            query = query.where(Expense.date <= end_date)
        query = query.group_by(
            Vehicle.id, Vehicle.license_plate, Vehicle.brand, Vehicle.model,
            Vehicle.year, Vehicle.purchase_price,
        ).order_by(func.coalesce(func.sum(Expense.amount), 0).desc())

        result = await self.db.execute(query)
        return [
            {
                "id": str(row[0]),
                "license_plate": row[1],
                "brand": row[2],
                "model": row[3],
                "year": row[4],
                "purchase_price": float(row[5]) if row[5] else 0,
                "total_expenses": float(row[6]),
                "tco": (float(row[5]) if row[5] else 0) + float(row[6]),
            }
            for row in result.all()
        ]

    async def fleet_utilization(self) -> dict:
        """Fleet utilization statistics."""
        result = await self.db.execute(
            select(Vehicle.status, func.count(Vehicle.id)).group_by(Vehicle.status)
        )
        counts = {str(row[0].value): row[1] for row in result.all()}
        total = sum(counts.values())
        active = counts.get("active", 0)
        return {
            "total": total,
            "active": active,
            "in_maintenance": counts.get("in_maintenance", 0),
            "decommissioned": counts.get("decommissioned", 0),
            "reserved": counts.get("reserved", 0),
            "utilization_rate": round(active / total * 100, 1) if total > 0 else 0,
        }

    async def fuel_consumption(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> list[dict]:
        """Fuel consumption per vehicle."""
        query = (
            select(
                Vehicle.id,
                Vehicle.license_plate,
                Vehicle.brand,
                Vehicle.model,
                func.sum(Expense.fuel_liters).label("total_liters"),
                func.sum(Expense.amount).label("total_cost"),
                func.count(Expense.id).label("refuel_count"),
            )
            .join(Expense, Expense.vehicle_id == Vehicle.id)
            .where(Expense.category == ExpenseCategory.FUEL)
            .where(Expense.fuel_liters.is_not(None))
        )
        if start_date:
            query = query.where(Expense.date >= start_date)
        if end_date:
            query = query.where(Expense.date <= end_date)
        query = query.group_by(
            Vehicle.id, Vehicle.license_plate, Vehicle.brand, Vehicle.model
        ).order_by(func.sum(Expense.fuel_liters).desc())

        result = await self.db.execute(query)
        return [
            {
                "id": str(row[0]),
                "license_plate": row[1],
                "brand": row[2],
                "model": row[3],
                "total_liters": round(float(row[4]), 1) if row[4] else 0,
                "total_cost": float(row[5]) if row[5] else 0,
                "refuel_count": row[6],
            }
            for row in result.all()
        ]

    async def expense_analysis(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> dict:
        """Comprehensive expense analysis."""
        base_filter = []
        if start_date:
            base_filter.append(Expense.date >= start_date)
        if end_date:
            base_filter.append(Expense.date <= end_date)

        # By category
        cat_result = await self.db.execute(
            select(Expense.category, func.sum(Expense.amount), func.count(Expense.id))
            .where(*base_filter)
            .group_by(Expense.category)
            .order_by(func.sum(Expense.amount).desc())
        )
        by_category = [
            {"category": str(r[0].value), "total": float(r[1]), "count": r[2]}
            for r in cat_result.all()
        ]

        # Monthly trends
        monthly_result = await self.db.execute(
            select(
                func.date_trunc("month", Expense.date).label("month"),
                func.sum(Expense.amount),
                func.count(Expense.id),
            )
            .where(*base_filter)
            .group_by("month")
            .order_by("month")
        )
        monthly = [
            {"month": str(r[0].date()), "total": float(r[1]), "count": r[2]}
            for r in monthly_result.all()
        ]

        # Grand total
        total_result = await self.db.execute(
            select(func.sum(Expense.amount), func.count(Expense.id)).where(*base_filter)
        )
        row = total_result.one()
        grand_total = float(row[0]) if row[0] else 0
        total_count = row[1]

        return {
            "by_category": by_category,
            "monthly": monthly,
            "grand_total": grand_total,
            "total_count": total_count,
        }

    async def maintenance_history(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> list[dict]:
        """Maintenance history report."""
        query = select(
            MaintenanceRecord.id,
            Vehicle.license_plate,
            Vehicle.brand,
            Vehicle.model,
            MaintenanceRecord.type,
            MaintenanceRecord.title,
            MaintenanceRecord.status,
            MaintenanceRecord.scheduled_date,
            MaintenanceRecord.completed_date,
            MaintenanceRecord.cost,
            MaintenanceRecord.service_provider,
        ).join(Vehicle, Vehicle.id == MaintenanceRecord.vehicle_id)

        if start_date:
            query = query.where(MaintenanceRecord.scheduled_date >= start_date)
        if end_date:
            query = query.where(MaintenanceRecord.scheduled_date <= end_date)

        query = query.order_by(MaintenanceRecord.scheduled_date.desc())
        result = await self.db.execute(query)
        return [
            {
                "id": str(r[0]),
                "license_plate": r[1],
                "brand": r[2],
                "model": r[3],
                "type": str(r[4].value),
                "title": r[5],
                "status": str(r[6].value),
                "scheduled_date": str(r[7]) if r[7] else "",
                "completed_date": str(r[8]) if r[8] else "",
                "cost": float(r[9]) if r[9] else 0,
                "service_provider": r[10] or "",
            }
            for r in result.all()
        ]

    # --- Export helpers ---

    async def export_tco_excel(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> bytes:
        data = await self.tco_report(start_date, end_date)
        exp = ExcelExporter("TCO Report")
        period = self._period_label(start_date, end_date)
        exp.add_title("Total Cost of Ownership Report", period)
        exp.add_headers(["License Plate", "Brand", "Model", "Year", "Purchase Price", "Total Expenses", "TCO"])
        for r in data:
            exp.add_row([r["license_plate"], r["brand"], r["model"], r["year"],
                         r["purchase_price"], r["total_expenses"], r["tco"]])
        if data:
            exp.add_summary_row(["", "", "", "TOTAL",
                                 sum(r["purchase_price"] for r in data),
                                 sum(r["total_expenses"] for r in data),
                                 sum(r["tco"] for r in data)])
        return exp.to_bytes()

    async def export_fuel_excel(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> bytes:
        data = await self.fuel_consumption(start_date, end_date)
        exp = ExcelExporter("Fuel Consumption")
        period = self._period_label(start_date, end_date)
        exp.add_title("Fuel Consumption Report", period)
        exp.add_headers(["License Plate", "Brand", "Model", "Total Liters", "Total Cost", "Refuel Count"])
        for r in data:
            exp.add_row([r["license_plate"], r["brand"], r["model"],
                         r["total_liters"], r["total_cost"], r["refuel_count"]])
        return exp.to_bytes()

    async def export_maintenance_excel(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> bytes:
        data = await self.maintenance_history(start_date, end_date)
        exp = ExcelExporter("Maintenance History")
        period = self._period_label(start_date, end_date)
        exp.add_title("Maintenance History Report", period)
        exp.add_headers(["License Plate", "Vehicle", "Type", "Title", "Status",
                         "Scheduled", "Completed", "Cost", "Service Provider"])
        for r in data:
            exp.add_row([r["license_plate"], f'{r["brand"]} {r["model"]}',
                         r["type"], r["title"], r["status"],
                         r["scheduled_date"], r["completed_date"],
                         r["cost"], r["service_provider"]])
        return exp.to_bytes()

    async def export_expense_csv(
        self, start_date: dt.date | None = None, end_date: dt.date | None = None
    ) -> bytes:
        analysis = await self.expense_analysis(start_date, end_date)
        exp = CSVExporter()
        exp.add_headers(["Category", "Total Amount", "Transaction Count"])
        for r in analysis["by_category"]:
            exp.add_row([r["category"], r["total"], r["count"]])
        return exp.to_bytes()

    @staticmethod
    def _period_label(start_date: dt.date | None, end_date: dt.date | None) -> str:
        if start_date and end_date:
            return f"Period: {start_date} — {end_date}"
        elif start_date:
            return f"From: {start_date}"
        elif end_date:
            return f"Until: {end_date}"
        return "All time"
