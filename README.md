# Truck Transport System (Flask + Supabase)

Backend API for a truck/transport booking system. Uses **Flask** and **Supabase** (PostgreSQL).  
You have already created the tables: **users**, **drivers**, **trucks**, **bookings** with this schema:

- **users**: id, created_at, name, email, phone, password (no `role` — stored in session)
- **trucks**: id, created_at, truck_number, model, capacity, driver_id
- **drivers**: id, created_at, name, phone, license_number, experience (optional: add `user_id` UUID to link driver to a user for driver login)
- **bookings**: id, created_at, customer_id, truck_id, pickup_location, drop_location, price, status

If you use driver trip updates, create the **trips** table (see below).

## Setup

1. **Python 3.10+** and a virtualenv:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Environment variables**

   Copy `.env.example` to `.env` and fill in:

   - `DATABASE_URL` — Supabase **Settings → Database → Connection string** (URI, with password).
   - `SECRET_KEY` — random string for Flask sessions.
   - Optionally `SUPABASE_URL` and `SUPABASE_KEY` if you add Supabase client later.

   **Never commit `.env` or share the secret/service role key.**

3. **Run the app**

   ```bash
   python app.py
   ```

   API: `http://localhost:5000`  
   Frontend can call `/api/*` (use credentials if using cookies).

## API Routes

| Method | Route | Description |
|--------|--------|-------------|
| POST | `/api/register` | Register (name, email, phone, password, role) |
| POST | `/api/login` | Login (email, password) |
| POST | `/api/logout` | Logout |
| GET | `/api/profile` | Current user (login required) |
| GET | `/api/trucks` | List trucks (login required) |
| POST | `/api/trucks` | Add truck (admin) |
| GET/PUT/DELETE | `/api/trucks/<id>` | Get/update/delete truck (admin for write) |
| POST | `/api/bookings` | Create booking (pickup_location, drop_location, price) |
| GET | `/api/bookings` | List bookings (own or all for admin) |
| GET | `/api/bookings/<id>` | Get one booking |
| PUT | `/api/bookings/<id>/assign` | Assign truck (admin), body: `{ "truck_id": "uuid" }` |
| GET | `/api/driver/trips` | Driver’s assigned trips (driver login) |
| PUT | `/api/driver/trip/update` | Update trip (booking_id, current_location, status) |

Booking **status**: `pending` → `assigned` → `in_transit` → `completed`.

## Trips table (for driver tracking)

If you use driver trip updates, create in Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS trips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  booking_id UUID NOT NULL REFERENCES bookings(id),
  start_time TIMESTAMPTZ DEFAULT NOW(),
  end_time TIMESTAMPTZ,
  current_location TEXT
);
```

## Flow

1. **Customer** → Registers/logs in → Creates **booking** (pickup, drop, price).
2. **Admin** → Assigns a **truck** to the booking.
3. **Driver** → Sees assigned trips → Updates status/location (`in_transit`, `completed`).
4. **System** → Tracks trip (optional: store `current_location` for tracking).

## Security

- Keep **secret key** and **database URL** in `.env` only; never in frontend or repo.
- Only the **publishable (anon) key** is safe for frontend; backend can use service role if needed.
- Rotate keys in **Supabase Dashboard → Settings → API** if exposed.

## Project structure

```
truck-system/
├── app.py
├── config.py
├── database.py
├── models/
│   ├── user.py, truck.py, booking.py, trip.py
├── routes/
│   ├── auth_routes.py, truck_routes.py, booking_routes.py, driver_routes.py
├── services/
│   ├── booking_service.py
├── templates/
├── static/
├── .env.example
└── requirements.txt
```
