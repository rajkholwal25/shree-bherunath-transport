"""Booking business logic: create booking, assign truck, price calculation placeholder."""
from models.booking import create_booking, assign_truck_to_booking, get_booking_by_id
from models.truck import get_truck_by_id, get_all_trucks


def create_booking_for_customer(customer_id, pickup_location, drop_location, price, truck_id=None):
    """Create a booking; optionally assign truck."""
    return create_booking(customer_id, pickup_location, drop_location, price, truck_id)


def assign_truck(booking_id, truck_id):
    """Assign truck to booking."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        return None, "Booking not found"
    truck = get_truck_by_id(truck_id)
    if not truck:
        return None, "Truck not found"
    return assign_truck_to_booking(booking_id, truck_id), None


def get_available_trucks():
    """List all trucks (no status column in schema)."""
    return get_all_trucks()
