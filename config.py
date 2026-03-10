"""Application configuration. Load from environment."""
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Secret key — backend only, never expose
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")  # Publishable key — safe for frontend

# Direct PostgreSQL connection (Supabase: Dashboard > Settings > Database > Connection string)
DATABASE_URL = os.getenv("DATABASE_URL", "")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
FLASK_ENV = os.getenv("FLASK_ENV", "development")

# Only this email gets admin role; no one can sign up as admin from the UI or API
SUPERADMIN_EMAIL = os.getenv("SUPERADMIN_EMAIL", "rajkholwal25.2@gmail.com").strip().lower()
