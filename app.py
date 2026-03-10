"""Flask app entry point. Truck / Transport system with Supabase."""
import os
import uuid
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_cors import CORS

from config import SECRET_KEY, SUPERADMIN_EMAIL
from database import close_connection
from models.admin import get_admin_by_email, verify_admin_password
from models.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password,
    set_reset_token,
    get_user_by_reset_token,
    update_password_and_clear_reset,
)
from email_sender import send_reset_email
from models.booking import (
    get_bookings_by_customer,
    get_all_bookings,
    get_bookings_by_status,
    create_booking,
    update_booking_status,
    update_booking_approve_with_driver,
    update_booking_reject,
    assign_truck_to_booking,
    get_bookings_by_customer_with_trucks,
    get_booking_by_id,
)
from models.truck import get_all_trucks, get_truck_by_id, create_truck, update_truck, delete_truck
from models.driver import create_driver, get_all_drivers, get_driver_by_id, update_driver, delete_driver
from models.route import create_route, get_all_routes, get_route_by_id, update_route, delete_route
from models.service import create_service, get_all_services, get_service_by_id, update_service, delete_service

# Routes
from routes.auth_routes import auth_bp
from routes.truck_routes import truck_bp
from routes.booking_routes import booking_bp
from routes.driver_routes import driver_bp


def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapped


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "warning")
            return redirect(url_for("login_page"))
        if session.get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return wrapped


def _valid_driver_uuid(s):
    """Return s if it's a valid UUID string, else None. Avoids invalid input for driver_id."""
    if not s or not s.strip():
        return None
    try:
        uuid.UUID(s.strip())
        return s.strip()
    except (ValueError, TypeError):
        return None


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = SECRET_KEY
    CORS(app, supports_credentials=True)

    # Lightweight auto-migrations (safe if already exist)
    try:
        from database import get_cursor
        with get_cursor() as cur:
            cur.execute("ALTER TABLE trucks ADD COLUMN IF NOT EXISTS image_url TEXT;")
            cur.execute("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS rejection_reason TEXT;")
            cur.execute("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS driver_id UUID;")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token TEXT;")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_expires TIMESTAMPTZ;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    from_location TEXT NOT NULL,
                    to_location TEXT NOT NULL,
                    hours NUMERIC(5,2),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    display_order INT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            cur.connection.commit()
            # Seed default services if empty
            cur.execute("SELECT COUNT(*) AS n FROM services")
            if cur.fetchone().get("n", 0) == 0:
                defaults = [
                    ("Full Truck Load (FTL)", "Our Full Truck Load service is ideal for customers who need an entire truck for their goods. This option ensures faster delivery, direct transportation, and maximum safety, as your cargo is not mixed with other shipments. It is perfect for bulk goods, business consignments, and large shipments requiring secure handling.", "✅"),
                    ("Part Load Service (LTL)", "Our Part Load service is designed for smaller shipments that do not require a full truck. You only pay for the space your goods occupy, making it a cost-effective and flexible solution. This service is ideal for small businesses and individual customers who want reliable transport at affordable rates.", "✅"),
                    ("Safe & Reliable Transportation", "We handle all types of goods with proper care and responsibility. Whether it is commercial cargo or general items, we ensure safe loading, secure transit, and timely delivery.", "📦"),
                ]
                for i, (title, desc, icon) in enumerate(defaults):
                    cur.execute(
                        "INSERT INTO services (title, description, icon, display_order) VALUES (%s, %s, %s, %s)",
                        (title, desc, icon, i),
                    )
                cur.connection.commit()
    except Exception:
        pass

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(truck_bp, url_prefix="/api")
    app.register_blueprint(booking_bp, url_prefix="/api")
    app.register_blueprint(driver_bp, url_prefix="/api")

    @app.route("/")
    def index():
        trucks = get_all_trucks()[:6]
        routes = get_all_routes()
        services = get_all_services()
        return render_template("index.html", trucks=trucks, routes=routes, services=services)

    @app.route("/login", methods=["GET", "POST"])
    def login_page():
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            if not email or not password:
                flash("Email and password are required.", "error")
                return render_template("login.html")

            # 1) Admin table login (highest priority)
            admin_row = get_admin_by_email(email)
            if admin_row and verify_admin_password(admin_row, password):
                session["user_id"] = email.strip().lower()  # admin table may not have uuid
                session["role"] = "admin"
                session["user_name"] = admin_row.get("name") or "Admin"
                flash("Welcome, Admin!", "success")
                return redirect(url_for("admin_dashboard"))

            # 2) Superadmin email fallback (via users table)
            user = get_user_by_email(email)
            if not user or not verify_password(user, password):
                flash("Invalid email or password.", "error")
                return render_template("login.html")
            session["user_id"] = str(user["id"])
            session["role"] = "admin" if email.strip().lower() == SUPERADMIN_EMAIL else user.get("role", "customer")
            session["user_name"] = user.get("name", "")
            flash("Welcome back!", "success")
            if session["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password_page():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            if not email:
                flash("Please enter your email.", "error")
                return redirect(url_for("forgot_password_page"))
            user, token = set_reset_token(email)
            if user and token:
                reset_url = url_for("reset_password_page", token=token, _external=True)
                send_reset_email(email, reset_url, user.get("name") or "")
            flash(
                "If an account exists for this email, we sent a reset link. Check your inbox (and spam).",
                "info",
            )
            return render_template("forgot_password_check_email.html", email=email)
        return render_template("forgot_password.html")

    @app.route("/reset-password", methods=["GET", "POST"])
    def reset_password_page():
        token = request.args.get("token") or (request.form.get("token") or "").strip()
        if not token:
            flash("Invalid or missing reset link.", "error")
            return redirect(url_for("login_page"))
        user = get_user_by_reset_token(token)
        if not user:
            flash("This reset link is invalid or has expired. Request a new one.", "error")
            return redirect(url_for("forgot_password_page"))
        if request.method == "POST":
            new_password = request.form.get("password") or ""
            confirm = request.form.get("confirm_password") or ""
            if len(new_password) < 6:
                flash("Password must be at least 6 characters.", "error")
                return render_template("reset_password.html", token=token)
            if new_password != confirm:
                flash("Passwords do not match.", "error")
                return render_template("reset_password.html", token=token)
            update_password_and_clear_reset(user["id"], new_password)
            flash("Password updated. You can log in with your new password.", "success")
            return redirect(url_for("login_page"))
        return render_template("reset_password.html", token=token)

    @app.route("/register", methods=["GET", "POST"])
    def register_page():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            role = request.form.get("role", "customer")
            if not name or not email or not password:
                flash("Name, email and password are required.", "error")
                return render_template("register.html")
            if role not in ("driver", "customer"):
                role = "customer"
            if role == "admin":
                role = "customer"
            if get_user_by_email(email):
                flash("This email is already registered.", "error")
                return render_template("register.html")
            user = create_user(name, email, phone, password, role)
            if not user:
                flash("Registration failed. Try again.", "error")
                return render_template("register.html")
            session["user_id"] = str(user["id"])
            session["role"] = "admin" if email.strip().lower() == SUPERADMIN_EMAIL else user.get("role", "customer")
            session["user_name"] = user.get("name", "")
            flash("Account created. Welcome!", "success")
            return redirect(url_for("dashboard"))
        return render_template("register.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))
        user = get_user_by_id(session["user_id"])
        return render_template("dashboard.html", user=user)

    @app.route("/trucks")
    def trucks_page():
        trucks = get_all_trucks()
        return render_template("trucks.html", trucks=trucks)

    @app.route("/trucks/<truck_id>/book", methods=["GET", "POST"])
    @login_required
    def book_truck(truck_id):
        truck = get_truck_by_id(truck_id)
        if not truck:
            flash("Truck not found.", "error")
            return redirect(url_for("trucks_page"))
        if request.method == "POST":
            pickup = (request.form.get("pickup_location") or "").strip()
            drop = (request.form.get("drop_location") or "").strip()
            try:
                price = float(request.form.get("price", 0))
            except (TypeError, ValueError):
                price = 0
            if not pickup or not drop:
                flash("Pickup and drop location are required.", "error")
                return redirect(url_for("book_truck", truck_id=truck_id))
            if price <= 0:
                flash("Please enter a valid price.", "error")
                return redirect(url_for("book_truck", truck_id=truck_id))
            booking = create_booking(session["user_id"], pickup, drop, price, truck_id=truck_id)
            if booking:
                flash("Booking request sent (pending approval).", "success")
                return redirect(url_for("bookings_page"))
            flash("Could not create booking. Try again.", "error")
            return redirect(url_for("book_truck", truck_id=truck_id))
        return render_template("book_truck.html", truck=truck)

    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        pending = get_bookings_by_status("pending")
        bookings = get_all_bookings()
        trucks = get_all_trucks()
        return render_template("admin_dashboard.html", pending=pending, bookings=bookings, trucks=trucks)

    @app.route("/admin/booking/<booking_id>/approve", methods=["GET", "POST"])
    @admin_required
    def admin_approve_booking(booking_id):
        booking = get_booking_by_id(booking_id)
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            driver_id = (request.form.get("driver_id") or "").strip() or None
            updated = update_booking_approve_with_driver(booking_id, driver_id)
            if updated:
                flash("Booking approved. Driver assigned." if driver_id else "Booking approved.", "success")
            else:
                flash("Could not approve booking.", "error")
            return redirect(url_for("admin_dashboard"))
        drivers = get_all_drivers()
        return render_template("admin_booking_approve.html", booking=booking, drivers=drivers)

    @app.route("/admin/booking/<booking_id>/reject", methods=["GET", "POST"])
    @admin_required
    def admin_reject_booking(booking_id):
        booking = get_booking_by_id(booking_id)
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            reason = (request.form.get("rejection_reason") or "").strip()
            updated = update_booking_reject(booking_id, reason)
            if updated:
                flash("Booking rejected. User will see the reason.", "info")
            else:
                flash("Could not reject booking.", "error")
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_booking_reject.html", booking=booking)

    @app.route("/admin/assign", methods=["POST"])
    @admin_required
    def admin_assign_truck():
        booking_id = (request.form.get("booking_id") or "").strip()
        truck_id = (request.form.get("truck_id") or "").strip()
        if not booking_id or not truck_id:
            flash("Please select a truck.", "error")
            return redirect(url_for("admin_dashboard"))
        updated = assign_truck_to_booking(booking_id, truck_id)
        if updated:
            flash("Truck assigned successfully.", "success")
        else:
            flash("Failed to assign truck.", "error")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/drivers", methods=["GET", "POST"])
    @admin_required
    def admin_drivers():
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            phone = (request.form.get("phone") or "").strip()
            license_number = (request.form.get("license_number") or "").strip()
            experience = (request.form.get("experience") or "").strip()
            if not name or not phone or not license_number:
                flash("Name, phone, and license number are required.", "error")
                return redirect(url_for("admin_drivers"))
            row = create_driver(name, phone, license_number, experience)
            if row:
                flash("Driver added.", "success")
            else:
                flash("Failed to add driver.", "error")
            return redirect(url_for("admin_drivers"))

        drivers = get_all_drivers()
        return render_template("admin_drivers.html", drivers=drivers)

    @app.route("/admin/drivers/<driver_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_driver_edit(driver_id):
        driver = get_driver_by_id(driver_id)
        if not driver:
            flash("Driver not found.", "error")
            return redirect(url_for("admin_drivers"))
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            phone = (request.form.get("phone") or "").strip()
            license_number = (request.form.get("license_number") or "").strip()
            experience = (request.form.get("experience") or "").strip()
            if not name or not phone or not license_number:
                flash("Name, phone, and license number are required.", "error")
                return redirect(url_for("admin_driver_edit", driver_id=driver_id))
            updated = update_driver(
                driver_id,
                name=name,
                phone=phone,
                license_number=license_number,
                experience=experience,
            )
            if updated:
                flash("Driver updated.", "success")
            else:
                flash("Failed to update driver.", "error")
            return redirect(url_for("admin_drivers"))
        return render_template("admin_driver_edit.html", driver=driver)

    @app.route("/admin/drivers/<driver_id>/delete", methods=["POST"])
    @admin_required
    def admin_driver_delete(driver_id):
        if delete_driver(driver_id):
            flash("Driver deleted.", "info")
        else:
            flash("Failed to delete driver.", "error")
        return redirect(url_for("admin_drivers"))

    @app.route("/admin/trucks", methods=["GET", "POST"])
    @admin_required
    def admin_trucks():
        if request.method == "POST":
            truck_number = (request.form.get("truck_number") or "").strip()
            model = (request.form.get("model") or "").strip()
            capacity = (request.form.get("capacity") or "").strip()
            image_url = (request.form.get("image_url") or "").strip() or None
            driver_id = _valid_driver_uuid(request.form.get("driver_id") or "")
            if not truck_number or not model or not capacity:
                flash("Truck number, model, and capacity are required.", "error")
                return redirect(url_for("admin_trucks"))
            row = create_truck(truck_number, model, capacity, driver_id=driver_id, image_url=image_url)
            if row:
                flash("Truck added.", "success")
            else:
                flash("Failed to add truck.", "error")
            return redirect(url_for("admin_trucks"))

        trucks = get_all_trucks()
        drivers = get_all_drivers()
        return render_template("admin_trucks.html", trucks=trucks, drivers=drivers)

    @app.route("/admin/trucks/<truck_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_truck_edit(truck_id):
        truck = get_truck_by_id(truck_id)
        if not truck:
            flash("Truck not found.", "error")
            return redirect(url_for("admin_trucks"))
        if request.method == "POST":
            truck_number = (request.form.get("truck_number") or "").strip()
            model = (request.form.get("model") or "").strip()
            capacity = (request.form.get("capacity") or "").strip()
            image_url = (request.form.get("image_url") or "").strip()
            driver_id = _valid_driver_uuid(request.form.get("driver_id") or "")
            if not truck_number or not model or not capacity:
                flash("Truck number, model, and capacity are required.", "error")
                return redirect(url_for("admin_truck_edit", truck_id=truck_id))
            updated = update_truck(
                truck_id,
                truck_number=truck_number,
                model=model,
                capacity=capacity,
                driver_id=driver_id,
                image_url=image_url or None,
            )
            if updated:
                flash("Truck updated.", "success")
            else:
                flash("Failed to update truck.", "error")
            return redirect(url_for("admin_trucks"))
        drivers = get_all_drivers()
        return render_template("admin_truck_edit.html", truck=truck, drivers=drivers)

    @app.route("/admin/trucks/<truck_id>/delete", methods=["POST"])
    @admin_required
    def admin_truck_delete(truck_id):
        if delete_truck(truck_id):
            flash("Truck deleted.", "info")
        else:
            flash("Failed to delete truck.", "error")
        return redirect(url_for("admin_trucks"))

    @app.route("/admin/routes", methods=["GET", "POST"])
    @admin_required
    def admin_routes():
        if request.method == "POST":
            from_loc = (request.form.get("from_location") or "").strip()
            to_loc = (request.form.get("to_location") or "").strip()
            hours_val = request.form.get("hours", "").strip()
            hours = None
            if hours_val:
                try:
                    hours = float(hours_val)
                except ValueError:
                    pass
            if not from_loc or not to_loc:
                flash("From and To locations are required.", "error")
                return redirect(url_for("admin_routes"))
            row = create_route(from_loc, to_loc, hours=hours)
            if row:
                flash("Route added.", "success")
            else:
                flash("Failed to add route.", "error")
            return redirect(url_for("admin_routes"))
        routes_list = get_all_routes()
        return render_template("admin_routes.html", routes=routes_list)

    @app.route("/admin/routes/<route_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_route_edit(route_id):
        route = get_route_by_id(route_id)
        if not route:
            flash("Route not found.", "error")
            return redirect(url_for("admin_routes"))
        if request.method == "POST":
            from_loc = (request.form.get("from_location") or "").strip()
            to_loc = (request.form.get("to_location") or "").strip()
            hours_val = request.form.get("hours", "").strip()
            hours = None
            if hours_val:
                try:
                    hours = float(hours_val)
                except ValueError:
                    pass
            if not from_loc or not to_loc:
                flash("From and To locations are required.", "error")
                return redirect(url_for("admin_route_edit", route_id=route_id))
            updated = update_route(route_id, from_location=from_loc, to_location=to_loc, hours=hours)
            if updated:
                flash("Route updated.", "success")
            else:
                flash("Failed to update route.", "error")
            return redirect(url_for("admin_routes"))
        return render_template("admin_route_edit.html", route=route)

    @app.route("/admin/routes/<route_id>/delete", methods=["POST"])
    @admin_required
    def admin_route_delete(route_id):
        if delete_route(route_id):
            flash("Route deleted.", "info")
        else:
            flash("Failed to delete route.", "error")
        return redirect(url_for("admin_routes"))

    @app.route("/admin/services", methods=["GET", "POST"])
    @admin_required
    def admin_services():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            description = (request.form.get("description") or "").strip()
            icon = (request.form.get("icon") or "").strip() or None
            if not title:
                flash("Title is required.", "error")
                return redirect(url_for("admin_services"))
            row = create_service(title, description, icon=icon)
            if row:
                flash("Service added.", "success")
            else:
                flash("Failed to add service.", "error")
            return redirect(url_for("admin_services"))
        services_list = get_all_services()
        return render_template("admin_services.html", services=services_list)

    @app.route("/admin/services/<service_id>/edit", methods=["GET", "POST"])
    @admin_required
    def admin_service_edit(service_id):
        service = get_service_by_id(service_id)
        if not service:
            flash("Service not found.", "error")
            return redirect(url_for("admin_services"))
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            description = (request.form.get("description") or "").strip()
            icon = (request.form.get("icon") or "").strip() or None
            if not title:
                flash("Title is required.", "error")
                return redirect(url_for("admin_service_edit", service_id=service_id))
            updated = update_service(service_id, title=title, description=description, icon=icon)
            if updated:
                flash("Service updated.", "success")
            else:
                flash("Failed to update service.", "error")
            return redirect(url_for("admin_services"))
        return render_template("admin_service_edit.html", service=service)

    @app.route("/admin/services/<service_id>/delete", methods=["POST"])
    @admin_required
    def admin_service_delete(service_id):
        if delete_service(service_id):
            flash("Service deleted.", "info")
        else:
            flash("Failed to delete service.", "error")
        return redirect(url_for("admin_services"))

    @app.route("/bookings", methods=["GET", "POST"])
    @login_required
    def bookings_page():
        if request.method == "POST":
            pickup = request.form.get("pickup_location", "").strip()
            drop = request.form.get("drop_location", "").strip()
            try:
                price = float(request.form.get("price", 0))
            except (TypeError, ValueError):
                price = 0
            if not pickup or not drop:
                flash("Pickup and drop location are required.", "error")
                return redirect(url_for("bookings_page"))
            if price <= 0:
                flash("Please enter a valid price.", "error")
                return redirect(url_for("bookings_page"))
            booking = create_booking(session["user_id"], pickup, drop, price, truck_id=None)
            if booking:
                flash("Booking created successfully.", "success")
            else:
                flash("Could not create booking. Try again.", "error")
            return redirect(url_for("bookings_page"))
        if session.get("role") == "admin":
            bookings = get_all_bookings()
        else:
            bookings = get_bookings_by_customer_with_trucks(session["user_id"])
        return render_template("bookings.html", bookings=bookings)

    @app.route("/logout", methods=["POST"])
    def logout_page():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.errorhandler(500)
    def handle_500(err):
        """Return JSON for API errors so frontend doesn't get HTML."""
        if request.path.startswith("/api/"):
            msg = getattr(err, "description", None) or str(err)
            return jsonify({"error": msg}), 500
        raise err

    @app.teardown_appcontext
    def teardown(exception=None):
        close_connection()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_ENV") == "development", port=5000)
