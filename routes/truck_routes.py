"""Truck CRUD. Admin only for create/update/delete."""
from flask import Blueprint, request, jsonify

from models.truck import create_truck, get_all_trucks, get_truck_by_id, update_truck, delete_truck
from routes.auth_routes import require_login, require_admin

truck_bp = Blueprint("trucks", __name__)


@truck_bp.route("/trucks", methods=["GET"])
@require_login
def list_trucks():
    """GET /api/trucks — list all trucks."""
    trucks = get_all_trucks()
    return jsonify({"trucks": trucks})


@truck_bp.route("/trucks", methods=["POST"])
@require_admin
def add_truck():
    """POST /api/trucks — truck_number, model, capacity, image_url, driver_id (optional)."""
    data = request.get_json() or {}
    truck_number = data.get("truck_number")
    model = data.get("model")
    capacity = data.get("capacity")
    driver_id = data.get("driver_id")
    image_url = data.get("image_url")

    if not truck_number or not model or not capacity:
        return jsonify({"error": "truck_number, model and capacity are required"}), 400

    truck = create_truck(truck_number, model, capacity, driver_id, image_url=image_url)
    if not truck:
        return jsonify({"error": "Failed to create truck"}), 500
    return jsonify({"truck": truck}), 201


@truck_bp.route("/trucks/<truck_id>", methods=["GET"])
@require_login
def get_truck(truck_id):
    """GET /api/trucks/<id>."""
    truck = get_truck_by_id(truck_id)
    if not truck:
        return jsonify({"error": "Truck not found"}), 404
    return jsonify({"truck": truck})


@truck_bp.route("/trucks/<truck_id>", methods=["PUT"])
@require_admin
def edit_truck(truck_id):
    """PUT /api/trucks/<id> — truck_number, model, capacity, driver_id, image_url (all optional)."""
    truck = get_truck_by_id(truck_id)
    if not truck:
        return jsonify({"error": "Truck not found"}), 404

    data = request.get_json() or {}
    updated = update_truck(
        truck_id,
        truck_number=data.get("truck_number"),
        model=data.get("model"),
        capacity=data.get("capacity"),
        driver_id=data.get("driver_id"),
        image_url=data.get("image_url"),
    )
    return jsonify({"truck": updated})


@truck_bp.route("/trucks/<truck_id>", methods=["DELETE"])
@require_admin
def remove_truck(truck_id):
    """DELETE /api/trucks/<id>."""
    if not get_truck_by_id(truck_id):
        return jsonify({"error": "Truck not found"}), 404
    delete_truck(truck_id)
    return jsonify({"message": "Truck deleted"}), 200
