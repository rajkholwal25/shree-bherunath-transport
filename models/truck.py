"""Truck model. Uses trucks table (id, created_at, truck_number, model, capacity, driver_id, image_url)."""
from database import get_cursor


def create_truck(truck_number, model, capacity, driver_id=None, image_url=None):
    """Insert truck. driver_id optional."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO trucks (truck_number, model, capacity, driver_id, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (truck_number, model, capacity, driver_id, image_url),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_all_trucks():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM trucks ORDER BY truck_number")
        return [dict(r) for r in cur.fetchall()]


def get_truck_by_id(truck_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM trucks WHERE id = %s", (truck_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_truck(truck_id, truck_number=None, model=None, capacity=None, driver_id=None, image_url=None, status=None):
    """Update truck by id. Only non-None fields are updated. (status ignored — not in table.)"""
    with get_cursor() as cur:
        updates = []
        args = []
        if truck_number is not None:
            updates.append("truck_number = %s")
            args.append(truck_number)
        if model is not None:
            updates.append("model = %s")
            args.append(model)
        if capacity is not None:
            updates.append("capacity = %s")
            args.append(capacity)
        if driver_id is not None:
            updates.append("driver_id = %s")
            args.append(driver_id)
        if image_url is not None:
            updates.append("image_url = %s")
            args.append(image_url)
        if not updates:
            return get_truck_by_id(truck_id)
        args.append(truck_id)
        cur.execute(
            "UPDATE trucks SET " + ", ".join(updates) + " WHERE id = %s RETURNING *",
            args,
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def delete_truck(truck_id):
    with get_cursor() as cur:
        cur.execute("DELETE FROM trucks WHERE id = %s RETURNING id", (truck_id,))
        row = cur.fetchone()
        cur.connection.commit()
        return row is not None
