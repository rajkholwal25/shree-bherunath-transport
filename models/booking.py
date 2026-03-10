"""Booking model. Uses bookings table (id, customer_id, truck_id, pickup_location, drop_location, price, status, created_at)."""
from database import get_cursor

# Booking statuses in this app:
# pending -> approved/rejected -> assigned -> in_transit -> completed
STATUSES = ("pending", "approved", "rejected", "assigned", "in_transit", "completed")


def create_booking(customer_id, pickup_location, drop_location, price, truck_id=None):
    """Create booking. status defaults to pending."""
    # Even if customer selects a truck, keep the request pending for admin approval.
    status = "pending"
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO bookings (customer_id, truck_id, pickup_location, drop_location, price, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (customer_id, truck_id, pickup_location, drop_location, float(price), status),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_booking_by_id(booking_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_bookings_by_customer(customer_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM bookings WHERE customer_id = %s ORDER BY created_at DESC",
            (customer_id,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_all_bookings():
    with get_cursor() as cur:
        cur.execute("SELECT * FROM bookings ORDER BY created_at DESC")
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_bookings_by_status(status: str):
    if status not in STATUSES:
        return []
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM bookings WHERE status = %s ORDER BY created_at DESC",
            (status,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def update_booking_status(booking_id, status):
    if status not in STATUSES:
        return None
    with get_cursor() as cur:
        cur.execute(
            "UPDATE bookings SET status = %s WHERE id = %s RETURNING *",
            (status, booking_id),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def update_booking_approve_with_driver(booking_id, driver_id=None):
    """Set status to approved and optionally assign driver."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE bookings SET status = 'approved', driver_id = %s WHERE id = %s RETURNING *",
            (driver_id or None, booking_id),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def update_booking_reject(booking_id, reason):
    """Set status to rejected and store rejection reason."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE bookings SET status = 'rejected', rejection_reason = %s WHERE id = %s RETURNING *",
            ((reason or "").strip() or None, booking_id),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_bookings_by_customer_with_trucks(customer_id):
    """Return customer bookings with truck and driver details when assigned."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT b.*,
                   t.truck_number AS truck_number,
                   t.model AS truck_model,
                   t.capacity AS truck_capacity,
                   d.name AS driver_name,
                   d.phone AS driver_phone
            FROM bookings b
            LEFT JOIN trucks t ON t.id = b.truck_id
            LEFT JOIN drivers d ON d.id = b.driver_id
            WHERE b.customer_id = %s
            ORDER BY b.created_at DESC
            """,
            (customer_id,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def assign_truck_to_booking(booking_id, truck_id):
    """Assign truck and set status to assigned."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE bookings SET truck_id = %s, status = 'assigned' WHERE id = %s AND status != 'rejected' RETURNING *",
            (truck_id, booking_id),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None
