"""User model and helpers. Uses users table (id, name, email, phone, password, created_at). Role column optional."""
import secrets
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_cursor


def create_user(name, email, phone, password, role="customer"):
    """Insert user. Role is stored in session only if 'role' column does not exist."""
    hashed = generate_password_hash(password)
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (name, email, phone, password)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, email, phone, created_at
            """,
            (name, email, phone, hashed),
        )
        row = cur.fetchone()
        cur.connection.commit()
        if not row:
            return None
        user = dict(row)
        user["role"] = role
        return user


def get_user_by_email(email):
    """Get user by email (for login)."""
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        d.setdefault("role", "customer")
        return d


def get_user_by_id(user_id):
    """Get user by id (without password)."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, email, phone, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        d.setdefault("role", "customer")
        return d


def verify_password(user, password):
    """Check plain password against stored hash."""
    return user and check_password_hash(user.get("password") or "", password)


def set_reset_token(email, expires_hours=2):
    """Set reset_token and reset_expires for user by email. Returns (user, token) or (None, None)."""
    user = get_user_by_email(email)
    if not user:
        return None, None
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    with get_cursor() as cur:
        cur.execute(
            "UPDATE users SET reset_token = %s, reset_expires = %s WHERE id = %s",
            (token, expires, user["id"]),
        )
        cur.connection.commit()
    return user, token


def get_user_by_reset_token(token):
    """Get user by valid reset token (not expired). Returns None if invalid."""
    if not token or not token.strip():
        return None
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, email, phone, created_at FROM users WHERE reset_token = %s AND reset_expires > NOW()",
            (token.strip(),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return dict(row)


def update_password_and_clear_reset(user_id, new_password):
    """Set new password and clear reset_token/reset_expires for user."""
    hashed = generate_password_hash(new_password)
    with get_cursor() as cur:
        cur.execute(
            "UPDATE users SET password = %s, reset_token = NULL, reset_expires = NULL WHERE id = %s",
            (hashed, user_id),
        )
        cur.connection.commit()
