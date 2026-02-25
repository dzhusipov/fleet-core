"""Generate seed data for FleetCore: 500+ vehicles, drivers, maintenance, expenses, contracts.

WARNING: This script creates demo users with a shared password (SeedPass!2024).
         Use only in development/staging environments.
"""

import asyncio
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.contract import Contract, ContractStatus, ContractType, PaymentFrequency
from app.models.driver import Driver, DriverStatus
from app.models.expense import Currency, Expense, ExpenseCategory
from app.models.maintenance import (
    MaintenanceRecord,
    MaintenanceStatus,
    MaintenanceType,
)
from app.models.user import User, UserRole
from app.models.vehicle import (
    BodyType,
    FuelType,
    TransmissionType,
    Vehicle,
    VehicleStatus,
)
from app.utils.security import hash_password

# ---- Configuration ----
NUM_VEHICLES = 520
NUM_DRIVERS = 220
NUM_MAINTENANCE = 1200
NUM_EXPENSES = 5500
NUM_CONTRACTS = 350

# Kazakhstan regions (2-digit codes)
KZ_REGIONS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"]
KZ_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Popular car brands/models in KZ
VEHICLES_DATA = [
    ("Toyota", "Camry", "sedan", "gasoline", 2.5),
    ("Toyota", "Corolla", "sedan", "gasoline", 1.6),
    ("Toyota", "Land Cruiser 200", "suv", "diesel", 4.5),
    ("Toyota", "Land Cruiser 300", "suv", "diesel", 3.3),
    ("Toyota", "RAV4", "suv", "gasoline", 2.0),
    ("Toyota", "Hilux", "pickup", "diesel", 2.4),
    ("Toyota", "Fortuner", "suv", "diesel", 2.8),
    ("Hyundai", "Tucson", "suv", "gasoline", 2.0),
    ("Hyundai", "Santa Fe", "suv", "diesel", 2.2),
    ("Hyundai", "Sonata", "sedan", "gasoline", 2.0),
    ("Hyundai", "Elantra", "sedan", "gasoline", 1.6),
    ("Hyundai", "Accent", "sedan", "gasoline", 1.4),
    ("Hyundai", "Creta", "suv", "gasoline", 1.6),
    ("Kia", "Sportage", "suv", "gasoline", 2.0),
    ("Kia", "K5", "sedan", "gasoline", 2.0),
    ("Kia", "Cerato", "sedan", "gasoline", 1.6),
    ("Kia", "Seltos", "suv", "gasoline", 1.6),
    ("Kia", "Carnival", "minivan", "diesel", 2.2),
    ("Chevrolet", "Cobalt", "sedan", "gasoline", 1.5),
    ("Chevrolet", "Tracker", "suv", "gasoline", 1.0),
    ("Chevrolet", "Monza", "sedan", "gasoline", 1.5),
    ("Lada", "Vesta", "sedan", "gasoline", 1.6),
    ("Lada", "Granta", "sedan", "gasoline", 1.6),
    ("Lada", "Niva Travel", "suv", "gasoline", 1.7),
    ("Skoda", "Octavia", "sedan", "gasoline", 1.4),
    ("Skoda", "Rapid", "sedan", "gasoline", 1.6),
    ("Volkswagen", "Polo", "sedan", "gasoline", 1.6),
    ("Volkswagen", "Tiguan", "suv", "gasoline", 2.0),
    ("Nissan", "Qashqai", "suv", "gasoline", 2.0),
    ("Nissan", "X-Trail", "suv", "gasoline", 2.5),
    ("Mitsubishi", "Outlander", "suv", "gasoline", 2.4),
    ("Mitsubishi", "Pajero Sport", "suv", "diesel", 2.4),
    ("Renault", "Duster", "suv", "gasoline", 2.0),
    ("Renault", "Logan", "sedan", "gasoline", 1.6),
    ("Mercedes-Benz", "E-Class", "sedan", "gasoline", 2.0),
    ("Mercedes-Benz", "Sprinter", "van", "diesel", 2.1),
    ("BMW", "5 Series", "sedan", "gasoline", 2.0),
    ("Isuzu", "D-Max", "pickup", "diesel", 3.0),
    ("GAZ", "Gazel Next", "van", "diesel", 2.8),
    ("GAZ", "Gazel Business", "van", "diesel", 2.8),
    ("Ford", "Transit", "van", "diesel", 2.2),
    ("Hyundai", "HD78", "truck", "diesel", 3.9),
    ("KAMAZ", "5490", "truck", "diesel", 11.9),
    ("MAN", "TGS", "truck", "diesel", 10.5),
    ("PAZ", "4234", "bus", "diesel", 4.4),
    ("Yutong", "ZK6122H9", "bus", "diesel", 8.9),
]

COLORS = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Green", "Brown", "Beige"]
DEPARTMENTS = [
    "Administration", "Logistics", "Sales", "Engineering", "IT", "HR",
    "Finance", "Operations", "Marketing", "Supply Chain", "Transport Pool",
    "Executive", "Field Service", "Maintenance Team", "Security",
]

SERVICE_PROVIDERS = [
    "Toyota Center Almaty", "Hyundai Auto Kazakhstan", "Kia Motors Nur-Sultan",
    "AutoMaster Service", "Bosch Car Service", "Shell Helix Center",
    "Mobil 1 Center", "Total Service Station", "FIT Auto",
    "German Auto Service", "Japan Car Service", "Korean Auto Center",
    "Quick Lube Express", "TechnoService KZ", "Euro Auto Repair",
]

FUEL_STATIONS = [
    "KazMunayGas", "Helios", "Sinooil", "Royal Petrol", "Shell",
    "Total Energies", "AQNIET", "Gazpromneft", "Rompetrol", "Lukoil",
]

# Kazakh first names (male and female)
KZ_FIRST_NAMES = [
    "Arman", "Nursultan", "Daulet", "Aibek", "Kanat", "Marat", "Ruslan",
    "Yerlan", "Bauyrzhan", "Serik", "Aidar", "Nurzhan", "Timur", "Daniyar",
    "Zhenis", "Askar", "Bolat", "Erbol", "Samat", "Kairat", "Amir",
    "Aliya", "Dinara", "Zarina", "Aigul", "Madina", "Saltanat", "Asel",
    "Gulnara", "Zhanna", "Raushan", "Ainur", "Kamila", "Laura", "Dana",
    "Aizhan", "Moldir", "Symbat", "Nurgul", "Akmaral", "Zhaniya",
]

# Kazakh last names
KZ_LAST_NAMES = [
    "Aitbayev", "Baymuratov", "Dzhakishev", "Ermagambetov", "Iskakov",
    "Kenzhebayev", "Muratov", "Nazarbayev", "Omarov", "Sarsenbayev",
    "Tokayev", "Urazov", "Zhanseitov", "Abdrakhmanov", "Bektemirov",
    "Dosymov", "Gabbasov", "Kairatov", "Mustafin", "Nurpeisov",
    "Rakhimov", "Serikbayev", "Tursynbayev", "Yergaliyev", "Zhumatov",
    "Almukhamedov", "Batyrbekov", "Galimov", "Kadyrbekov", "Mazhitov",
]


def gen_plate() -> str:
    """Generate a Kazakhstan-format license plate: 123 ABC 01."""
    digits = f"{random.randint(1, 999):03d}"
    letters = "".join(random.choices(KZ_LETTERS, k=3))
    region = random.choice(KZ_REGIONS)
    return f"{digits} {letters} {region}"


def gen_vin() -> str:
    """Generate a random 17-character VIN."""
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ1234567890"
    return "".join(random.choices(chars, k=17))


def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


async def seed():
    print("Starting seed data generation...")
    used_plates = set()
    used_vins = set()

    async with AsyncSessionLocal() as db:
        # Check if we already have data
        existing = await db.execute(select(Vehicle.id).limit(5))
        if existing.scalars().first():
            print("Database already has vehicle data. Skipping seed.")
            return

        # Get admin user for created_by references
        admin_result = await db.execute(select(User).where(User.role == UserRole.ADMIN).limit(1))
        admin = admin_result.scalar_one_or_none()
        admin_id = admin.id if admin else None

        # ---- Create additional users ----
        print("Creating users...")
        users = []
        for i in range(5):
            user = User(
                email=f"manager{i+1}@fleetcore.kz",
                username=f"manager{i+1}",
                full_name=f"{random.choice(KZ_FIRST_NAMES)} {random.choice(KZ_LAST_NAMES)}",
                hashed_password=hash_password("SeedPass!2024"),
                role=UserRole.FLEET_MANAGER,
                is_active=True,
                language="ru",
            )
            db.add(user)
            users.append(user)
        for i in range(3):
            user = User(
                email=f"viewer{i+1}@fleetcore.kz",
                username=f"viewer{i+1}",
                full_name=f"{random.choice(KZ_FIRST_NAMES)} {random.choice(KZ_LAST_NAMES)}",
                hashed_password=hash_password("SeedPass!2024"),
                role=UserRole.VIEWER,
                is_active=True,
                language="ru",
            )
            db.add(user)
            users.append(user)
        await db.flush()
        all_user_ids = [u.id for u in users]
        if admin_id:
            all_user_ids.append(admin_id)

        # ---- Create drivers ----
        print(f"Creating {NUM_DRIVERS} drivers...")
        drivers = []
        for i in range(NUM_DRIVERS):
            today = date.today()
            license_exp = rand_date(today - timedelta(days=30), today + timedelta(days=365 * 3))
            medical_exp = rand_date(today - timedelta(days=30), today + timedelta(days=365 * 2))
            hire_d = rand_date(date(2015, 1, 1), today - timedelta(days=30))
            status = random.choices(
                [DriverStatus.ACTIVE, DriverStatus.ON_LEAVE, DriverStatus.TERMINATED],
                weights=[85, 10, 5],
            )[0]
            fname = random.choice(KZ_FIRST_NAMES)
            lname = random.choice(KZ_LAST_NAMES)
            driver = Driver(
                full_name=f"{fname} {lname}",
                employee_id=f"EMP-{1000 + i}",
                phone=f"+7 {random.randint(700, 778)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}",
                email=f"{fname.lower()}.{lname.lower()}@fleetcore.kz",
                license_number=f"{random.randint(10, 99)}{random.randint(100000, 999999):06d}",
                license_category=random.choice(["B", "B, C", "B, C, D", "B, C, CE", "D"]),
                license_expiry=license_exp,
                medical_expiry=medical_exp,
                hire_date=hire_d,
                department=random.choice(DEPARTMENTS),
                status=status,
            )
            db.add(driver)
            drivers.append(driver)
        await db.flush()
        active_driver_ids = [d.id for d in drivers if d.status == DriverStatus.ACTIVE]

        # ---- Create vehicles ----
        print(f"Creating {NUM_VEHICLES} vehicles...")
        vehicles = []
        for i in range(NUM_VEHICLES):
            brand, model, body, fuel, engine = random.choice(VEHICLES_DATA)
            year = random.randint(2016, 2025)
            purchase = rand_date(date(year, 1, 1), min(date(year, 12, 31), date.today()))
            status = random.choices(
                [VehicleStatus.ACTIVE, VehicleStatus.IN_MAINTENANCE, VehicleStatus.DECOMMISSIONED, VehicleStatus.RESERVED],
                weights=[80, 10, 5, 5],
            )[0]
            plate = gen_plate()
            while plate in used_plates:
                plate = gen_plate()
            used_plates.add(plate)
            vin = gen_vin()
            while vin in used_vins:
                vin = gen_vin()
            used_vins.add(vin)

            transmission = random.choice(list(TransmissionType))
            mileage = random.randint(5000, 350000) if year < 2025 else random.randint(0, 30000)
            price = Decimal(str(random.randint(3_000_000, 45_000_000)))
            assigned_driver = random.choice(active_driver_ids) if status == VehicleStatus.ACTIVE and random.random() > 0.3 else None

            vehicle = Vehicle(
                license_plate=plate,
                vin=vin,
                brand=brand,
                model=model,
                year=year,
                color=random.choice(COLORS),
                body_type=BodyType(body),
                fuel_type=FuelType(fuel),
                engine_volume=engine,
                transmission=transmission,
                seats=random.choice([2, 5, 7, 8, 15, 25, 45]) if body in ("bus", "minivan") else random.choice([2, 5, 7]),
                purchase_date=purchase,
                purchase_price=price,
                current_mileage=mileage,
                status=status,
                assigned_driver_id=assigned_driver,
                department=random.choice(DEPARTMENTS),
                notes=None,
            )
            db.add(vehicle)
            vehicles.append(vehicle)
        await db.flush()
        vehicle_ids = [v.id for v in vehicles]
        active_vehicle_ids = [v.id for v in vehicles if v.status in (VehicleStatus.ACTIVE, VehicleStatus.IN_MAINTENANCE)]

        # ---- Create maintenance records ----
        print(f"Creating {NUM_MAINTENANCE} maintenance records...")
        maint_titles = {
            MaintenanceType.SCHEDULED_SERVICE: [
                "ТО-1: замена масла и фильтров",
                "ТО-2: полное обслуживание",
                "ТО-3: замена масла, фильтров, свечей",
                "ТО-4: капитальное обслуживание",
                "Замена масла и масляного фильтра",
                "Плановое ТО по регламенту",
            ],
            MaintenanceType.REPAIR: [
                "Ремонт подвески",
                "Замена тормозных колодок",
                "Замена аккумулятора",
                "Ремонт генератора",
                "Замена ремня ГРМ",
                "Ремонт рулевой рейки",
                "Замена радиатора",
            ],
            MaintenanceType.INSPECTION: [
                "Технический осмотр",
                "Диагностика двигателя",
                "Проверка тормозной системы",
                "Инспекция ходовой части",
            ],
            MaintenanceType.TIRE_CHANGE: [
                "Сезонная замена шин (зимние)",
                "Сезонная замена шин (летние)",
                "Замена повреждённой шины",
                "Балансировка колёс",
            ],
            MaintenanceType.BODY_REPAIR: [
                "Покраска бампера",
                "Удаление вмятин",
                "Замена лобового стекла",
                "Полировка кузова",
            ],
            MaintenanceType.RECALL: [
                "Отзывная кампания: подушки безопасности",
                "Отзывная кампания: обновление ПО",
            ],
        }

        today = date.today()
        for _ in range(NUM_MAINTENANCE):
            mtype = random.choice(list(MaintenanceType))
            title = random.choice(maint_titles[mtype])
            scheduled = rand_date(today - timedelta(days=365), today + timedelta(days=90))
            status = random.choices(
                [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.COMPLETED, MaintenanceStatus.CANCELLED],
                weights=[25, 10, 55, 10],
            )[0]
            completed = scheduled + timedelta(days=random.randint(0, 5)) if status == MaintenanceStatus.COMPLETED else None
            cost = Decimal(str(random.randint(5000, 500000))) if status == MaintenanceStatus.COMPLETED else None
            vid = random.choice(active_vehicle_ids)

            record = MaintenanceRecord(
                vehicle_id=vid,
                type=mtype,
                title=title,
                description=f"Описание работ: {title}",
                status=status,
                scheduled_date=scheduled,
                completed_date=completed,
                mileage_at_service=random.randint(10000, 300000),
                next_service_mileage=random.randint(10000, 300000) + 10000 if random.random() > 0.5 else None,
                next_service_date=scheduled + timedelta(days=random.randint(90, 365)) if random.random() > 0.5 else None,
                cost=cost,
                service_provider=random.choice(SERVICE_PROVIDERS),
                performed_by=f"{random.choice(KZ_FIRST_NAMES)} {random.choice(KZ_LAST_NAMES)}",
                created_by=random.choice(all_user_ids) if all_user_ids else None,
            )
            db.add(record)

        # ---- Create expenses ----
        print(f"Creating {NUM_EXPENSES} expense records...")
        for _ in range(NUM_EXPENSES):
            category = random.choices(
                list(ExpenseCategory),
                weights=[40, 10, 15, 8, 5, 5, 5, 3, 5, 4],
            )[0]
            vid = random.choice(active_vehicle_ids)
            exp_date = rand_date(today - timedelta(days=365), today)

            if category == ExpenseCategory.FUEL:
                liters = round(random.uniform(20, 80), 1)
                price_per_liter = Decimal(str(round(random.uniform(180, 320), 2)))
                amount = Decimal(str(round(float(price_per_liter) * liters, 2)))
                fuel_type = random.choice(["AI-92", "AI-95", "AI-98", "DT"])
                mileage_at_refuel = random.randint(10000, 300000)
                vendor = random.choice(FUEL_STATIONS)
            else:
                liters = None
                price_per_liter = None
                amount = Decimal(str(random.randint(1000, 300000)))
                fuel_type = None
                mileage_at_refuel = None
                vendor = random.choice(SERVICE_PROVIDERS + FUEL_STATIONS) if category in (ExpenseCategory.PARTS, ExpenseCategory.SERVICE) else None

            expense = Expense(
                vehicle_id=vid,
                driver_id=random.choice(active_driver_ids) if random.random() > 0.3 else None,
                category=category,
                amount=amount,
                currency=Currency.KZT,
                date=exp_date,
                description=f"{category.value}: запись расхода",
                vendor=vendor,
                fuel_liters=liters,
                fuel_price_per_liter=price_per_liter,
                fuel_type=fuel_type,
                mileage_at_refuel=mileage_at_refuel,
                created_by=random.choice(all_user_ids) if all_user_ids else None,
            )
            db.add(expense)

        # ---- Create contracts ----
        print(f"Creating {NUM_CONTRACTS} contracts...")
        contractors = {
            ContractType.LEASING: ["KazFinance Leasing", "Halyk Leasing", "BCC Leasing", "Freedom Finance Leasing"],
            ContractType.RENTAL: ["AutoRent KZ", "Hertz Kazakhstan", "Europcar KZ", "Sixt Kazakhstan"],
            ContractType.INSURANCE_CASCO: ["Nomad Insurance", "Eurasia Insurance", "Halyk Insurance", "Freedom Insurance"],
            ContractType.INSURANCE_OSAGO: ["Nomad Insurance", "Eurasia Insurance", "Halyk Insurance", "KompetenzGarant"],
            ContractType.WARRANTY: ["Toyota Kazakhstan", "Hyundai Kazakhstan", "Kia Kazakhstan", "Official Dealer"],
            ContractType.SERVICE_CONTRACT: SERVICE_PROVIDERS[:8],
        }

        for _ in range(NUM_CONTRACTS):
            ctype = random.choice(list(ContractType))
            start = rand_date(today - timedelta(days=365 * 2), today)
            duration = random.choice([90, 180, 365, 365 * 2, 365 * 3])
            end = start + timedelta(days=duration)
            status = ContractStatus.ACTIVE if end >= today else ContractStatus.EXPIRED
            if status == ContractStatus.ACTIVE and random.random() < 0.1:
                status = ContractStatus.PENDING_RENEWAL

            contract = Contract(
                vehicle_id=random.choice(vehicle_ids),
                type=ctype,
                contractor=random.choice(contractors[ctype]),
                contract_number=f"{ctype.value[:3].upper()}-{random.randint(10000, 99999)}",
                start_date=start,
                end_date=end,
                amount=Decimal(str(random.randint(50000, 5_000_000))),
                payment_frequency=random.choice(list(PaymentFrequency)),
                status=status,
                auto_renew=random.random() > 0.7,
                notes=None,
                created_by=random.choice(all_user_ids) if all_user_ids else None,
            )
            db.add(contract)

        await db.commit()
        print(f"\nSeed data created successfully!")
        print(f"  Users:        {len(users)} new (+ existing)")
        print(f"  Drivers:      {NUM_DRIVERS}")
        print(f"  Vehicles:     {NUM_VEHICLES}")
        print(f"  Maintenance:  {NUM_MAINTENANCE}")
        print(f"  Expenses:     {NUM_EXPENSES}")
        print(f"  Contracts:    {NUM_CONTRACTS}")


if __name__ == "__main__":
    asyncio.run(seed())
