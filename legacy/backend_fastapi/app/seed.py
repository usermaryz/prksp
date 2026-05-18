from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Carrier, Order, PickingTask, Product, Shipment, User, WarehouseZone
from app.security import hash_password


def _now() -> datetime:
    return datetime.now(UTC)


def seed_if_empty(db: Session) -> None:
    if db.query(User).first():
        return

    ts = _now()

    users = [
        User(
            username="admin",
            email="admin@local",
            hashed_password=hash_password("admin"),
            full_name="Иван Петров",
            phone="+79160000001",
            role="admin",
            is_active=True,
            created_at=ts,
            last_login_at=None,
        ),
        User(
            username="manager",
            email="mgr@local",
            hashed_password=hash_password("manager"),
            full_name="Анна Смирнова",
            role="manager",
            is_active=True,
            created_at=ts,
            last_login_at=None,
        ),
        User(
            username="picker",
            email="pick@local",
            hashed_password=hash_password("picker"),
            full_name="Сергей Козлов",
            role="picker",
            is_active=True,
            created_at=ts,
            last_login_at=None,
        ),
        User(
            username="driver",
            email="drv@local",
            hashed_password=hash_password("driver"),
            full_name="Олег Волков",
            role="driver",
            is_active=True,
            created_at=ts,
            last_login_at=None,
        ),
    ]
    db.add_all(users)

    zones = [
        WarehouseZone(code="A", name="Приёмка и буфер", capacity=2400, used=1100),
        WarehouseZone(code="B", name="Хранение", capacity=5000, used=3950),
        WarehouseZone(code="C", name="Зона сборки", capacity=900, used=780),
        WarehouseZone(code="D", name="Отгрузка", capacity=650, used=410),
    ]
    db.add_all(zones)

    carriers = [
        Carrier(name="СДЭК"),
        Carrier(name="Boxberry"),
        Carrier(name="Почта России"),
    ]
    db.add_all(carriers)
    db.flush()

    demo_products = [
        ("SKU-001", "Ноутбук 15\"", 89990, 35, "B-03-01"),
        ("SKU-002", "Клавиатура механическая", 7990, 12, "B-03-07"),
        ("SKU-003", "Наушники TWS", 4990, 8, "B-03-07"),
        ("SKU-004", "Кабель USB-C", 590, 200, "A-01-02"),
        ("SKU-005", "Стойка мониторная", 3200, 4, "B-03-09"),
        ("SKU-006", "Коврик для мыши", 890, 60, "A-02-03"),
        ("SKU-007", "SSD 1TB", 6990, 24, "B-03-05"),
        ("SKU-008", "Коробка упаковочная М", 45, 500, "A-05-02"),
        ("SKU-009", "Вентилятор 120 мм", 1190, 18, "B-03-06"),
        ("SKU-010", "Портативное зарядное 20W", 1490, 30, "A-06-03"),
        ("SKU-011", "Картридж офисный набор", 450, 16, None),
        ("SKU-012", "Маркер упаковочный", 120, 90, None),
    ]
    for sku, name, price, stock, loc in demo_products:
        db.add(
            Product(
                sku=sku,
                barcode=sku.replace("SKU-", "BC"),
                name=name,
                description=None,
                price=float(price),
                stock=stock,
                location=loc,
                category_id=None,
                created_at=ts,
                updated_at=ts,
            )
        )

    orders_data = [
        ("ООО Альфа", "+79260111223", "Москва, ул. Советская, д. 10", "pending", 12450.0, 3),
        ("Елена Никитина", "+79151112233", "СПб, пр. Энгельса, д. 4", "picking", 7800.0, 4),
        ("ИП Сидоров", "+79037889900", "Казань, ул. Баумана, д. 2", "picking", 2100.0, 2),
        ("ООО Техносервис", "+74957889977", "Нижний Новгород, ул. Советская, д. 1", "shipped", 9320.5, 5),
        ("Марина О.", "+79851230045", "Самара, ул. Осипенко, д. 8 к. 3", "delivered", 450.0, 1),
    ]

    picking_jobs: list[PickingTask] = []
    for idx, (cn, cp, addr, status, total, icount) in enumerate(orders_data, start=1):
        onum = f"ORD-2026-{idx:03d}"
        o = Order(
            order_number=onum,
            customer_name=cn,
            customer_phone=cp,
            customer_address=addr,
            status=status,
            priority="normal" if idx % 2 else "high",
            total=float(total),
            items_count=icount,
            shipping_ready=False,
            created_at=ts - timedelta(hours=3 * idx),
            updated_at=ts,
        )
        db.add(o)
        db.flush()

        if status == "picking":
            picking_jobs.append(
                PickingTask(
                    order_id=o.id,
                    status="pending",
                    assigned_to=None,
                    progress=35 if idx == 3 else 0,
                    items_count=max(1, icount - 1),
                    created_at=ts - timedelta(minutes=30 * idx),
                    completed_at=None,
                )
            )

    db.add_all(picking_jobs)
    db.flush()

    shipped = db.query(Order).filter(Order.status == "shipped").first()
    if shipped:
        est = (ts + timedelta(days=2)).strftime("%d.%m.%Y")
        ship = Shipment(
            order_id=shipped.id,
            carrier_id=carriers[0].id,
            tracking_number="SDEK-TRACK-982341",
            delivery_method="courier",
            status="in_transit",
            recipient_name=shipped.customer_name,
            delivery_address=shipped.customer_address,
            estimated_delivery=est,
            created_at=ts - timedelta(days=1),
        )
        db.add(ship)

    db.commit()
