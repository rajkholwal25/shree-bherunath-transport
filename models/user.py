"""User model and helpers. Uses users table (id, name, email, phone, password, created_at). Role column optional."""
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
