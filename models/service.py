"""Service cards for Our Services section. Table: services (id, title, description, icon, display_order, created_at)."""
from database import get_cursor


def create_service(title: str, description: str, icon: str = None):
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO services (title, description, icon)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (title.strip(), (description or "").strip(), (icon or "").strip() or None),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_all_services():
    """Return each service once; deduplicate by title so the same card does not repeat."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM services ORDER BY display_order NULLS LAST, created_at")
        seen = set()
        result = []
        for r in cur.fetchall():
            d = dict(r)
            key = (d.get("title") or "").strip()
            if key and key not in seen:
                seen.add(key)
                result.append(d)
        return result


def get_service_by_id(service_id: str):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_service(service_id: str, title=None, description=None, icon=None, display_order=None):
    with get_cursor() as cur:
        updates = []
        args = []
        if title is not None:
            updates.append("title = %s")
            args.append(title.strip())
        if description is not None:
            updates.append("description = %s")
            args.append(description.strip())
        if icon is not None:
            updates.append("icon = %s")
            args.append((icon or "").strip() or None)
        if display_order is not None:
            updates.append("display_order = %s")
            args.append(display_order)
        if not updates:
            return get_service_by_id(service_id)
        args.append(service_id)
        cur.execute(
            "UPDATE services SET " + ", ".join(updates) + " WHERE id = %s RETURNING *",
            args,
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def delete_service(service_id: str) -> bool:
    with get_cursor() as cur:
        cur.execute("DELETE FROM services WHERE id = %s RETURNING id", (service_id,))
        row = cur.fetchone()
        cur.connection.commit()
        return row is not None
