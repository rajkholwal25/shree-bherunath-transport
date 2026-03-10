"""Booking routes: create, list, get one. Admin can assign truck."""
from flask import Blueprint, request, jsonify

from models.booking import (
    create_booking,
    get_booking_by_id,
    get_bookings_by_customer,
    get_all_bookings,
    assign_truck_to_booking,
)
from routes.auth_routes import require_login, require_admin

booking_bp = Blueprint("bookings", __name__)


@booking_bp.route("/bookings", methods=["POST"])
@require_login
def add_booking():
    """POST /api/bookings — pickup_location, drop_location, price, truck_id (optional)."""
    data = request.get_json() or {}
    pickup = data.get("pickup_location") or data.get("pickup")
    drop = data.get("drop_location") or data.get("drop")
    price = data.get("price")
    truck_id = data.get("truck_id")

    if not pickup or not drop or price is None:
        return jsonify({"error": "pickup_location, drop_location and price are required"}), 400

    customer_id = request.session["user_id"]
    booking = create_booking(customer_id, pickup, drop, price, truck_id)
    if not booking:
        return jsonify({"error": "Failed to create booking"}), 500
    return jsonify({"booking": booking}), 201


@booking_bp.route("/bookings", methods=["GET"])
@require_login
def list_bookings():
    """GET /api/bookings — all for admin, own for customer."""
    if request.session.get("role") == "admin":
        bookings = get_all_bookings()
    else:
        bookings = get_bookings_by_customer(request.session["user_id"])
    return jsonify({"bookings": bookings})


@booking_bp.route("/bookings/<booking_id>", methods=["GET"])
@require_login
def get_booking(booking_id):
    """GET /api/bookings/<id>."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    # Customer can only see own; admin can see all
    if request.session.get("role") != "admin" and str(booking["customer_id"]) != request.session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({"booking": booking})


@booking_bp.route("/bookings/<booking_id>/assign", methods=["PUT"])
@require_admin
def assign_truck(booking_id):
    """PUT /api/bookings/<id>/assign — body: { "truck_id": "uuid" }."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    data = request.get_json() or {}
    truck_id = data.get("truck_id")
    if not truck_id:
        return jsonify({"error": "truck_id required"}), 400
    updated = assign_truck_to_booking(booking_id, truck_id)
    return jsonify({"booking": updated})
