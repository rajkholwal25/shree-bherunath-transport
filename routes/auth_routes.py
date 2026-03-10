"""Auth routes: register, login, profile."""
from flask import Blueprint, request, jsonify, session

from config import SUPERADMIN_EMAIL
from models.admin import get_admin_by_email, verify_admin_password
from models.user import create_user, get_user_by_email, get_user_by_id, verify_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/register — name, email, phone, password, role (optional, default customer)."""
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    role = data.get("role", "customer")

    if not all([name, email, password]):
        return jsonify({"error": "name, email and password are required"}), 400
    if role not in ("driver", "customer"):
        role = "customer"
    if role == "admin":
        role = "customer"

    if get_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409

    user = create_user(name, email, phone or "", password, role)
    if not user:
        return jsonify({"error": "Registration failed"}), 500

    # Don't store password in session
    session["user_id"] = str(user["id"])
    session["role"] = user.get("role", "customer")
    return jsonify({"message": "Registered", "user": user}), 201


def _effective_role(user):
    """Admin only for superadmin email; otherwise use stored role."""
    email = (user.get("email") or "").strip().lower()
    return "admin" if email == SUPERADMIN_EMAIL else user.get("role", "customer")


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/login — email, password."""
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    admin_row = get_admin_by_email(email)
    if admin_row and verify_admin_password(admin_row, password):
        session["user_id"] = (email or "").strip().lower()
        session["role"] = "admin"
        out = {k: v for k, v in admin_row.items() if k != "password"}
        out["role"] = "admin"
        return jsonify({"message": "Logged in", "user": out})

    user = get_user_by_email(email)
    if not user or not verify_password(user, password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = str(user["id"])
    session["role"] = _effective_role(user)
    out = {k: v for k, v in user.items() if k != "password"}
    out["role"] = session["role"]
    return jsonify({"message": "Logged in", "user": out})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/logout."""
    session.clear()
    return jsonify({"message": "Logged out"})


def require_login(f):
    """Decorator: require session user_id."""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return wrapped


def require_admin(f):
    """Decorator: require admin role."""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Login required"}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "Admin only"}), 403
        return f(*args, **kwargs)
    return wrapped


@auth_bp.route("/profile", methods=["GET"])
@require_login
def profile():
    """GET /api/profile — current user (requires login)."""
    if session.get("role") == "admin":
        admin_row = get_admin_by_email(session.get("user_id"))
        if not admin_row:
            session.clear()
            return jsonify({"error": "Admin not found"}), 404
        out = {k: v for k, v in admin_row.items() if k != "password"}
        out["role"] = "admin"
        return jsonify({"user": out})

    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404
    user["role"] = session.get("role", "customer")
    return jsonify({"user": user})
