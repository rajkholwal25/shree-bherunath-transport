"""Driver routes: list assigned trips, update trip status/location."""
import psycopg2
from flask import Blueprint, request, jsonify

from database import get_cursor
from models.booking import get_booking_by_id, update_booking_status
from models.trip import get_trip_by_booking, create_trip, update_trip_location, end_trip
from routes.auth_routes import require_login

driver_bp = Blueprint("driver", __name__)


def _get_driver_id():
    """Driver id for current user. Returns None if drivers table has no user_id column or no row."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT id FROM drivers WHERE user_id = %s", (request.session["user_id"],))
            row = cur.fetchone()
            return str(row["id"]) if row else None
    except psycopg2.ProgrammingError:
        return None


@driver_bp.route("/driver/trips", methods=["GET"])
@require_login
def driver_trips():
    """GET /api/driver/trips — trips for current driver (bookings where driver's truck is assigned)."""
    driver_id = _get_driver_id()
    if not driver_id:
        return jsonify({"trips": [], "message": "No driver profile or no assigned trips"})

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT b.* FROM bookings b
            JOIN trucks t ON t.id = b.truck_id
            WHERE t.driver_id = %s AND b.status IN ('assigned', 'in_transit')
            ORDER BY b.created_at DESC
            """,
            (driver_id,),
        )
        bookings = [dict(r) for r in cur.fetchall()]

    out = []
    for b in bookings:
        trip = get_trip_by_booking(b["id"])
        out.append({"booking": b, "trip": trip})
    return jsonify({"trips": out})


@driver_bp.route("/driver/trip/update", methods=["PUT"])
@require_login
def update_trip():
    """PUT /api/driver/trip/update — booking_id, current_location (optional), status (optional: in_transit, completed)."""
    data = request.get_json() or {}
    booking_id = data.get("booking_id")
    current_location = data.get("current_location")
    status = data.get("status")

    if not booking_id:
        return jsonify({"error": "booking_id required"}), 400

    booking = get_booking_by_id(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    driver_id = _get_driver_id()
    if not driver_id:
        return jsonify({"error": "Driver profile required"}), 403
    # Verify this booking's truck is assigned to this driver
    with get_cursor() as cur:
        cur.execute(
            "SELECT id FROM trucks WHERE id = %s AND driver_id = %s",
            (str(booking["truck_id"]), driver_id),
        )
        if not cur.fetchone():
            return jsonify({"error": "Not your assigned trip"}), 403

    if status == "in_transit":
        update_booking_status(booking_id, "in_transit")
        trip = get_trip_by_booking(booking_id)
        if not trip:
            create_trip(booking_id, current_location or "")
        elif current_location:
            update_trip_location(trip["id"], current_location)
    elif status == "completed":
        update_booking_status(booking_id, "completed")
        trip = get_trip_by_booking(booking_id)
        if trip:
            end_trip(trip["id"])
    elif current_location:
        trip = get_trip_by_booking(booking_id)
        if trip:
            update_trip_location(trip["id"], current_location)

    updated_booking = get_booking_by_id(booking_id)
    trip = get_trip_by_booking(booking_id)
    return jsonify({"booking": updated_booking, "trip": trip})
