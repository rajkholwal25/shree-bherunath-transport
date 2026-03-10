"""Admin model. Uses admin table (name, email, phone, password)."""
import psycopg2
from werkzeug.security import check_password_hash

from database import get_cursor


def get_admin_by_email(email: str):
    """Return admin row as dict or None. Handles missing table gracefully."""
    if not email:
        return None
    try:
        with get_cursor() as cur:
            cur.execute("SELECT * FROM admin WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None
    except psycopg2.Error:
        return None


def verify_admin_password(admin_row: dict, password: str) -> bool:
    """
    Accepts either:
    - Werkzeug hashed password (recommended), or
    - plain-text password (matches exactly) for legacy/manual inserts.
    """
    if not admin_row or not password:
        return False
    stored = admin_row.get("password") or ""
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:"):
        return check_password_hash(stored, password)
    return stored == password

