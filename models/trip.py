"""Trip model for driver tracking. Uses trips table (id, booking_id, start_time, end_time, current_location)."""
from database import get_cursor


def create_trip(booking_id, current_location=None):
    """Start a trip for a booking."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO trips (booking_id, start_time, current_location)
            VALUES (%s, NOW(), %s)
            RETURNING *
            """,
            (booking_id, current_location or ""),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def get_trip_by_booking(booking_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM trips WHERE booking_id = %s ORDER BY start_time DESC LIMIT 1", (booking_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def get_trips_by_driver(driver_id):
    """Trips for bookings where the driver's truck is assigned."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT t.*, b.pickup_location, b.drop_location, b.status AS booking_status
            FROM trips t
            JOIN bookings b ON b.id = t.booking_id
            JOIN trucks tr ON tr.id = b.truck_id
            WHERE tr.driver_id = %s
            ORDER BY t.start_time DESC
            """,
            (driver_id,),
        )
        return [dict(r) for r in cur.fetchall()]


def update_trip_location(trip_id, current_location):
    with get_cursor() as cur:
        cur.execute(
            "UPDATE trips SET current_location = %s WHERE id = %s RETURNING *",
            (current_location, trip_id),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None


def end_trip(trip_id):
    """Set end_time for trip (use database now())."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE trips SET end_time = NOW() WHERE id = %s RETURNING *",
            (trip_id,),
        )
        row = cur.fetchone()
        cur.connection.commit()
        return dict(row) if row else None
