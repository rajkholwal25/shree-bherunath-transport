"""Popular routes for homepage. Table: routes (id, from_location, to_location, hours, created_at)."""
from database import get_cursor


def create_route(from_location: str, to_location: str, hours=None):
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO routes (from_location, to_location, hours)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (from_location.strip(), to_location.strip(), hours),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_all_routes():
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM routes ORDER BY from_location, to_location"
        )
        return [dict(r) for r in cur.fetchall()]


def get_route_by_id(route_id: str):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM routes WHERE id = %s", (route_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_route(route_id: str, from_location=None, to_location=None, hours=None):
    with get_cursor() as cur:
        updates = []
        args = []
        if from_location is not None:
            updates.append("from_location = %s")
            args.append(from_location.strip())
        if to_location is not None:
            updates.append("to_location = %s")
            args.append(to_location.strip())
        if hours is not None:
            updates.append("hours = %s")
            args.append(hours)
        if not updates:
            return get_route_by_id(route_id)
        args.append(route_id)
        cur.execute(
            "UPDATE routes SET " + ", ".join(updates) + " WHERE id = %s RETURNING *",
            args,
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def delete_route(route_id: str) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM routes WHERE id = %s RETURNING id", (route_id,))
        row = cur.fetchone()
        cur.connection.commit()
        return row is not None
