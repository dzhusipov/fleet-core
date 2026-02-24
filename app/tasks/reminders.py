from datetime import date, timedelta

from app.database import get_sync_db
from app.models.contract import Contract, ContractStatus
from app.models.driver import Driver, DriverStatus
from app.models.maintenance import MaintenanceRecord, MaintenanceStatus
from app.tasks.celery_app import celery_app


@celery_app.task
def check_maintenance_reminders():
    """Check for upcoming/overdue maintenance and notify fleet managers."""
    db = get_sync_db()
    try:
        today = date.today()
        upcoming = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.status == MaintenanceStatus.SCHEDULED,
            MaintenanceRecord.scheduled_date <= today + timedelta(days=14),
            MaintenanceRecord.scheduled_date >= today,
        ).all()

        overdue = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.status == MaintenanceStatus.SCHEDULED,
            MaintenanceRecord.scheduled_date < today,
        ).all()

        # TODO: Send notifications for upcoming/overdue maintenance
        return {"upcoming": len(upcoming), "overdue": len(overdue)}
    finally:
        db.close()


@celery_app.task
def check_contract_expiry():
    """Check for expiring contracts."""
    db = get_sync_db()
    try:
        today = date.today()
        expiring = db.query(Contract).filter(
            Contract.status == ContractStatus.ACTIVE,
            Contract.end_date <= today + timedelta(days=30),
            Contract.end_date >= today,
        ).all()
        return {"expiring_contracts": len(expiring)}
    finally:
        db.close()


@celery_app.task
def check_driver_document_expiry():
    """Check for expiring driver licenses and medical certificates."""
    db = get_sync_db()
    try:
        today = date.today()
        deadline = today + timedelta(days=30)

        expiring_licenses = db.query(Driver).filter(
            Driver.status == DriverStatus.ACTIVE,
            Driver.license_expiry <= deadline,
            Driver.license_expiry >= today,
        ).all()

        expiring_medicals = db.query(Driver).filter(
            Driver.status == DriverStatus.ACTIVE,
            Driver.medical_expiry <= deadline,
            Driver.medical_expiry >= today,
        ).all()

        return {"expiring_licenses": len(expiring_licenses), "expiring_medicals": len(expiring_medicals)}
    finally:
        db.close()


@celery_app.task
def expire_overdue_contracts():
    """Auto-expire contracts past their end date."""
    db = get_sync_db()
    try:
        today = date.today()
        overdue = db.query(Contract).filter(
            Contract.status == ContractStatus.ACTIVE,
            Contract.end_date < today,
        ).all()
        for contract in overdue:
            contract.status = ContractStatus.EXPIRED
        db.commit()
        return {"expired": len(overdue)}
    finally:
        db.close()
