# Deploy Shree Bherunath Transport (Flask + Supabase)

Your database is already on **Supabase**, so you only need to deploy the Flask app and point it to your existing database.

---

## 1. Prepare the project

### 1.1 Production dependencies

Add **gunicorn** for production (already in `requirements.txt` below). Create/update:

**requirements.txt** should include:
```
flask>=3.0.0
psycopg2-binary>=2.9.9
flask-cors>=4.0.0
python-dotenv>=1.0.0
werkzeug>=3.0.0
gunicorn>=21.0.0
```

### 1.2 Environment variables (production)

Set these on your hosting platform (do **not** commit `.env` to Git):

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase Postgres URI, e.g. `postgresql://postgres:YOUR_PASSWORD@db.xxxx.supabase.co:5432/postgres` |
| `SECRET_KEY` | Long random string for sessions (e.g. `openssl rand -hex 32`) |
| `SUPERADMIN_EMAIL` | Admin email (e.g. `rajkholwal25.2@gmail.com`) |
| `FLASK_ENV` | Set to `production` (optional; some hosts set this automatically) |

Optional if you use Supabase APIs elsewhere: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_ANON_KEY`.

### 1.3 Push code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## 2. Option A: Deploy on Render (recommended)

1. Go to [render.com](https://render.com) and sign up / log in.
2. **New → Web Service**.
3. Connect your **GitHub** repo (e.g. `bhopu` or your repo name).
4. Configure:
   - **Name:** e.g. `shree-bherunath-transport`
   - **Region:** Choose nearest to your users.
   - **Runtime:** **Python 3**.
   - **Build command:**  
     `pip install -r requirements.txt`
   - **Start command:**  
     `gunicorn -w 2 -b 0.0.0.0:$PORT "app:app"`
     - If your app lives in a subfolder, use e.g. `gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app()"` and ensure the module path is correct (see below).
5. **Environment:**
   - Add `DATABASE_URL`, `SECRET_KEY`, `SUPERADMIN_EMAIL` (and optional Supabase vars).
   - For Supabase, if your connection string has special characters in the password, use the **URI** from Supabase Dashboard (it’s already encoded).
6. Click **Create Web Service**. Render will build and deploy. Your app will be at `https://YOUR-SERVICE.onrender.com`.

**Note:** On Render, the app object might need to be the callable. If your `app.py` exposes `app = create_app()`, the start command above is correct. If you only have `create_app()`, use:
`gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app()"`  
(and in code ensure the WSGI server gets the app: `application = create_app()` or `app = create_app()`).

---

## 3. Option B: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign up (e.g. with GitHub).
2. **New Project → Deploy from GitHub repo** and select your repo.
3. Railway will detect Python. Add a **start command** in the service settings:
   - **Start command:**  
     `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
4. In **Variables**, add:
   - `DATABASE_URL`, `SECRET_KEY`, `SUPERADMIN_EMAIL` (and optional Supabase vars).
5. Deploy. Railway will give you a URL like `https://xxx.up.railway.app`.

---

## 4. Option C: Deploy on a VPS (Ubuntu)

If you use a server (DigitalOcean, AWS EC2, etc.):

### 4.1 On the server

```bash
# Install Python 3, pip, and (optional) nginx
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# Clone your repo (or upload files)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 4.2 Virtual env and run with Gunicorn

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env with DATABASE_URL, SECRET_KEY, SUPERADMIN_EMAIL
export FLASK_ENV=production
gunicorn -w 2 -b 127.0.0.1:5000 "app:app"
```

### 4.3 Run as a service (so it restarts on reboot)

Create `/etc/systemd/system/shree-transport.service`:

```ini
[Unit]
Description=Shree Bherunath Transport Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/repo
Environment="PATH=/path/to/your/repo/venv/bin"
EnvironmentFile=/path/to/your/repo/.env
ExecStart=/path/to/your/repo/venv/bin/gunicorn -w 2 -b 127.0.0.1:5000 "app:app"
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable shree-transport
sudo systemctl start shree-transport
```

Use **nginx** as a reverse proxy in front of `127.0.0.1:5000` and add SSL (e.g. Let’s Encrypt).

---

## 5. Connect a GoDaddy domain

After your app is live (e.g. on Render or Railway), you can use a domain you buy from **GoDaddy** so users open `https://yourdomain.com` instead of `https://yourservice.onrender.com`.

### Step 1: Deploy the app first

Deploy on **Render** or **Railway** (see sections 2 or 3). Note your app URL, e.g.:

- Render: `https://shree-bherunath-transport.onrender.com`
- Railway: `https://your-app.up.railway.app`

### Step 2: Add custom domain in your host

**On Render**

1. Open your **Web Service** → **Settings** → **Custom Domains**.
2. Click **Add Custom Domain**.
3. Enter your domain, e.g. `shreebherunathtransport.com` or `www.shreebherunathtransport.com`.
4. Render will show you what to set in DNS (see Step 3). Usually:
   - For **www**: CNAME record: `www` → `your-service.onrender.com`
   - For **root (apex)** domain: A record or ALIAS/ANAME (Render gives the exact target).

**On Railway**

1. Open your **project** → **Settings** → **Domains** (or **Networking**).
2. Click **Add custom domain** and enter your domain.
3. Railway will show the CNAME or A record target. Copy it for Step 3.

### Step 3: Point GoDaddy DNS to your app

1. Log in to **GoDaddy** → **My Products** → your domain → **DNS** or **Manage DNS**.
2. Add or edit records as your host (Render/Railway) told you:

**If you use “www” (e.g. www.yourdomain.com):**

| Type  | Name | Value (example)                    | TTL  |
|-------|------|-------------------------------------|------|
| CNAME | www  | `your-service.onrender.com`        | 600  |

(Use the exact host name Render or Railway gave you.)

**If you use root domain only (e.g. yourdomain.com):**

- **Render:** Add the **A record** Render shows (often their IP or use their “redirect” setup).
- **Railway:** Add the CNAME or A target they provide for the root domain.
- On GoDaddy: **Name** = `@` (or leave blank for root), **Type** = A or CNAME, **Value** = target from Render/Railway.

3. **Save** the DNS changes. Propagation can take from a few minutes up to 24–48 hours.

### Step 4: SSL (HTTPS)

- **Render** and **Railway** issue a free SSL certificate when your custom domain is correctly pointed. No extra step in GoDaddy.
- After DNS has propagated, your site should open as `https://yourdomain.com` (or `https://www.yourdomain.com`).

### Step 5: Optional – redirect root to www (or vice versa)

- If you use **www**, you can redirect **yourdomain.com** → **www.yourdomain.com** (or the opposite) from your hosting dashboard (Render/Railway) or in GoDaddy (e.g. “Forwarding”).

### Quick checklist

1. Deploy app on Render or Railway.
2. Buy domain on GoDaddy (or use one you already have).
3. In Render/Railway: add custom domain and note the DNS target.
4. In GoDaddy DNS: add CNAME (for www) or A/ALIAS (for root) pointing to that target.
5. Wait for DNS to propagate; HTTPS will work automatically on Render/Railway.

---

## 6. Supabase checklist

- Use the **connection string** from **Supabase Dashboard → Settings → Database → Connection string (URI)**. Replace the password placeholder with your actual DB password (if it has special characters, the URI from the dashboard is usually already encoded).
- Ensure your **hosting platform’s IP** is allowed to connect (Supabase often allows all by default; if you use IP allowlist, add the platform’s outbound IPs or use a static IP if the host provides one).

---

## 7. After deployment

1. Open the deployed URL and test: Login, Register, Admin login, Bookings, Assign truck/driver, Reject with reason.
2. If you use a **custom domain** (e.g. from GoDaddy), follow **Section 5** to connect it; then update any links in your app (e.g. WhatsApp, footer) to use the new domain if needed.
3. Keep **SECRET_KEY** strong and secret; rotate it if it was ever exposed.
4. For production, set `FLASK_ENV=production` (or equivalent) so debug mode is off.

---

## Quick reference

| Platform | Build | Start command |
|----------|--------|----------------|
| Render | `pip install -r requirements.txt` | `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` |
| Railway | (auto) | `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` |
| VPS | `pip install -r requirements.txt` | `gunicorn -w 2 -b 127.0.0.1:5000 app:app` |

Replace `app:app` with `app:create_app()` if your app only exposes a factory and the host expects a callable.
