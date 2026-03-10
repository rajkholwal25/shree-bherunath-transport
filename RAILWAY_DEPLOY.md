# Deploy on Railway – Step-by-Step

Use this guide to deploy **Shree Bherunath Transport** on Railway (in addition to or instead of Render). Your app will get a URL like `https://shree-bherunath-transport.up.railway.app`.

---

## Before you start

- [ ] Code is on **GitHub** (e.g. repo `shree-bherunath-transport` or `bhopu`).
- [ ] You have the **pooler** `DATABASE_URL` from Supabase (Transaction pooler, port 6543).  
  **Do not use** the direct `db.xxx.supabase.co:5432` URI – use the pooler so Railway can reach the DB.
- [ ] You have **SECRET_KEY** and **SUPERADMIN_EMAIL** (same as for Render).

---

## STEP 1: Open Railway and sign in

1. Go to **[railway.app](https://railway.app)**.
2. Click **Login** or **Start a New Project**.
3. Choose **Login with GitHub** and authorize Railway.

---

## STEP 2: Create a project from GitHub

1. On the dashboard, click **New Project**.
2. Select **Deploy from GitHub repo** (or **Add GitHub repo**).
3. If asked, connect your GitHub account and grant access.
4. Choose your repo (e.g. **shree-bherunath-transport** or **bhopu**).
5. Railway will create a project and start a first deploy (it may fail until we set the start command and variables – that’s OK).

---

## STEP 3: Configure the service

1. Click your **service** (the card that represents the repo).
2. Open **Settings** (or the **Settings** tab).

### Build

- **Build Command:**  
  `pip install -r requirements.txt`  
  (Railway may auto-detect this for Python; if it does, you can leave it blank.)
- **Root Directory:** leave **blank** (app is in repo root).
- **Watch Paths:** leave default (or blank).

### Start / Run

- **Start Command** (or **Run Command**): set explicitly to  
  `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`  
  Railway provides `$PORT`; your app listens on it.

If your project has a **Procfile** with `web: gunicorn ...`, Railway might use it. If the app doesn’t start, set the **Start Command** as above.

---

## STEP 4: Add environment variables

1. In the same service, open **Variables** (or **Environment** / **Env**).
2. Click **Add Variable** (or **New Variable**) and add each of these.  
   Use the **same values** as on Render (or from your `.env`).

| Variable | Example / note |
|----------|-----------------|
| `DATABASE_URL` | Pooler URI, e.g. `postgresql://postgres.giuacdksqjuumxxzbixo:Mohitmeena%402002@aws-1-ap-south-1.pooler.supabase.com:6543/postgres` |
| `SECRET_KEY` | Long random string (e.g. from `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `SUPERADMIN_EMAIL` | e.g. `rajkholwal25.2@gmail.com` |
| `FLASK_ENV` | `production` |
| `SUPABASE_URL` | Your Supabase project URL (optional, if app uses it) |
| `SUPABASE_KEY` | Supabase secret key (optional) |
| `SUPABASE_ANON_KEY` | Supabase anon key (optional) |

3. Save. Railway will redeploy when variables change (depending on your settings).

---

## STEP 5: Get your public URL

1. In the service, open **Settings** or **Networking** (or **Deployments**).
2. Under **Networking** / **Public Networking**, click **Generate Domain** (or **Add Domain**).
3. Railway will assign a URL like `https://shree-bherunath-transport.up.railway.app` (or a random name). You can often rename the service to get a nicer subdomain.
4. Open that URL in the browser to test.

---

## STEP 6: Test the app

- Open the homepage, register, log in, and try admin login with **SUPERADMIN_EMAIL**.
- If you get **500** or **database errors**, check **Deployments** → latest deploy → **View Logs**. Use the **pooler** `DATABASE_URL` (port 6543), not the direct DB URL.

---

## Quick reference

| Item | Value |
|------|--------|
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` |
| **Required variables** | `DATABASE_URL` (pooler), `SECRET_KEY`, `SUPERADMIN_EMAIL` |
| **DATABASE_URL** | Must use Supabase **Transaction pooler** (e.g. `...pooler.supabase.com:6543/postgres`) |

---

## Railway vs Render (free tier)

| | Railway | Render |
|--|--------|--------|
| **Free tier** | Often a monthly credit (e.g. $5); check [railway.app/pricing](https://railway.app/pricing). | 750 hrs/month; service spins down after ~15 min idle. |
| **Cold starts** | Usually fewer if within credit. | First request after idle can be slow. |
| **Setup** | GitHub → New Project → repo → Variables + Start command. | GitHub → Web Service → repo → Env + Build/Start. |

You can run the same app on **both** Render and Railway; use the same **pooler** `DATABASE_URL` and env vars on each.
