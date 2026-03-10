"""Driver model. Uses drivers table (id, created_at, name, phone, license_number, experience)."""
from database import get_cursor


def create_driver(name: str, phone: str, license_number: str, experience: str):
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO drivers (name, phone, license_number, experience)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (name, phone, license_number, experience),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_all_drivers():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM drivers ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]


def get_driver_by_id(driver_id: str):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM drivers WHERE id = %s", (driver_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_driver(driver_id: str, name=None, phone=None, license_number=None, experience=None):
    with get_cursor() as cur:
        updates = []
        args = []
        if name is not None:
            updates.append("name = %s")
            args.append(name)
        if phone is not None:
            updates.append("phone = %s")
            args.append(phone)
        if license_number is not None:
            updates.append("license_number = %s")
            args.append(license_number)
        if experience is not None:
            updates.append("experience = %s")
            args.append(experience)
        if not updates:
            return get_driver_by_id(driver_id)
        args.append(driver_id)
        cur.execute(
            "UPDATE drivers SET " + ", ".join(updates) + " WHERE id = %s RETURNING *",
            args,
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def delete_driver(driver_id: str) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM drivers WHERE id = %s RETURNING id", (driver_id,))
        row = cur.fetchone()
        cur.connection.commit()
        return row is not None

