# Deploy Shree Bherunath Transport – Complete Step-by-Step Guide

Follow these steps in order. Your app will be live at a URL like `https://shree-bherunath-transport.onrender.com`.

---

## Before you start

- [ ] Your code is **pushed to GitHub** (you already did this).
- [ ] You have a **Supabase** project with the database set up (users, admin, trucks, drivers, bookings, routes, services).
- [ ] You have your **Supabase database password** and can open the Supabase Dashboard.

---

## STEP 1: Get your production values

You will need these in Step 5. Open a notepad and fill them as you go.

### 1.1 DATABASE_URL (from Supabase) – use **Connection pooler** for Render

**Important:** Render cannot reach Supabase’s **direct** DB host (`db.xxx.supabase.co:5432`). Use the **Connection pooler** URI instead.

1. Go to **[supabase.com](https://supabase.com)** → log in → open your project.
2. Click **Settings** (gear) → **Database**.
3. Scroll to **Connection string**. You may see **URI**, **Session pooler**, **Transaction pooler**.
4. Choose **Transaction pooler** (or **Session pooler**) – **not** the direct **URI** that uses `db.xxxx.supabase.co`.
   - Pooler URIs look like: `postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`
   - Direct (do **not** use on Render): `postgresql://...@db.xxxx.supabase.co:5432/postgres`
5. Copy the **pooler** URI and replace the password placeholder with your **actual database password** (use `%40` for `@` in the password if needed).
6. Paste the full URI into your notepad as **DATABASE_URL**.

**Tip:** If the password has special characters (e.g. `@`), encode `@` as `%40` in the URI.

### 1.2 SECRET_KEY (for Flask sessions)

1. Open **PowerShell** (or Git Bash) and run:
   ```powershell
   openssl rand -hex 32
   ```
   If `openssl` is not found, use an online generator and create a long random string (32+ characters), or run in Python:
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Copy the output and label it **SECRET_KEY** in your notepad.

### 1.3 SUPERADMIN_EMAIL

- Use the email that should have admin access (e.g. **rajkholwal25@gmail.com**).
- Write it in your notepad as **SUPERADMIN_EMAIL**.

---

## STEP 2: Sign up / log in on Render

1. Go to **[render.com](https://render.com)**.
2. Click **Get Started for Free** (or **Sign In** if you have an account).
3. Choose **Sign up with GitHub** and authorize Render to access your GitHub account.
4. After login, you should see the Render dashboard.

---

## STEP 3: Create a new Web Service

1. On the Render dashboard, click **New +** (top right).
2. Click **Web Service**.
3. You will see “Create a new Web Service” and a list of your GitHub repos.

---

## STEP 4: Connect your GitHub repo

1. If your repo (**bhopu** or whatever you named it) is not in the list, click **Configure account** and connect the GitHub account that has the repo.
2. Find your repository in the list and click **Connect** next to it.
3. Render will load the next screen with build and deploy settings.

---

## STEP 5: Configure the Web Service

Fill in these fields exactly.

### 5.1 Basic settings

| Field | What to enter |
|--------|----------------|
| **Name** | `shree-bherunath-transport` (or any name; this becomes part of your URL). |
| **Region** | Choose the one **closest to your users** (e.g. Singapore if users are in India). |
| **Branch** | `main` (or the branch you push to). |
| **Root Directory** | Leave **blank** (your app is in the repo root). |

### 5.2 Build & Deploy

| Field | What to enter |
|--------|----------------|
| **Runtime** | **Python 3**. |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` |

**Important:** Type the Start Command exactly as above. Render will set `$PORT` for you.

### 5.3 Environment variables

1. Scroll to **Environment** or **Environment Variables**.
2. Click **Add Environment Variable** and add these **one by one**:

| Key | Value | Notes |
|-----|--------|--------|
| `DATABASE_URL` | (paste the full Supabase URI from Step 1.1) | No spaces; paste as one line. |
| `SECRET_KEY` | (paste the value from Step 1.2) | Keep it secret. |
| `SUPERADMIN_EMAIL` | (e.g. rajkholwal25@gmail.com) | The email that gets admin access. |

3. Optional but good for production:
   - `FLASK_ENV` = `production`

4. **Optional – send password reset link by email (free):** To email the reset link instead of showing it on the page, add:
   - `RESEND_API_KEY` = your API key from [resend.com/api-keys](https://resend.com/api-keys) (free tier: 100 emails/day)
   - `RESEND_FROM` = `Shree Bherunath Transport <onboarding@resend.dev>` (or your verified domain email later)

5. Do **not** add your `.env` file here; only add the variables in the table above (and optional ones) using the Render form.

---

## STEP 6: Deploy

1. Click **Create Web Service** (or **Deploy**).
2. Render will:
   - Clone your repo
   - Run `pip install -r requirements.txt`
   - Start your app with the Start Command
3. You will see **Logs**; wait until you see something like “Your service is live at …”.

**First deploy can take 2–5 minutes.** If the build fails, check the logs for errors (e.g. missing package, wrong Start Command).

---

## STEP 7: Get your live URL

1. At the top of your service page, you will see a URL like:
   ```text
   https://shree-bherunath-transport.onrender.com
   ```
2. Click it to open your site.

---

## STEP 8: Test the deployed app

1. **Home page** – Opens without errors.
2. **Register** – Create a new user account.
3. **Login** – Log in with that user.
4. **Admin** – Log in with your **SUPERADMIN_EMAIL** (and the password you set for that user in the database). Check admin dashboard, bookings, drivers, trucks.
5. **Book a truck** – As a user, place a booking; as admin, approve/reject and assign driver if applicable.

If anything fails (e.g. “500 error”, “database connection”), check **Render → your service → Logs** for the error message. Most often it’s a wrong `DATABASE_URL` or missing env var.

---

## Summary checklist

| Step | What you did |
|------|----------------|
| 1 | Got `DATABASE_URL`, `SECRET_KEY`, `SUPERADMIN_EMAIL` |
| 2 | Signed up / logged in at Render with GitHub |
| 3 | New → Web Service |
| 4 | Connected your GitHub repo (bhopu) |
| 5 | Name, Region, Build: `pip install -r requirements.txt`, Start: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`, added env vars |
| 6 | Created Web Service and waited for deploy |
| 7 | Opened the live URL |
| 8 | Tested login, register, admin, bookings |

---

## After deployment: updates

When you change code and push to GitHub:

1. Push to your `main` branch:
   ```bash
   git add .
   git commit -m "Your change message"
   git push
   ```
2. Render will **automatically** detect the push and redeploy. Check the **Logs** or **Events** tab to see the new deploy.

---

## Optional: custom domain (e.g. GoDaddy)

To use your own domain (e.g. `www.yourdomain.com`):

1. In Render: open your **Web Service** → **Settings** → **Custom Domains** → **Add Custom Domain** → enter your domain. Render will show the **CNAME** or **A** record to use.
2. In GoDaddy (or your DNS provider): go to **DNS** for the domain and add the record Render gave you (e.g. CNAME `www` → `shree-bherunath-transport.onrender.com`).
3. Wait for DNS to propagate (minutes to a few hours). Render will issue a free SSL certificate so `https://www.yourdomain.com` works.

Full details (including root domain and SSL) are in **DEPLOYMENT.md** (Section 5).

---

## Troubleshooting

| Problem | What to check |
|--------|----------------|
| Build failed | Logs on Render: missing package? Fix `requirements.txt` and push again. |
| Application failed to start | Start Command must be exactly: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app` (and your entry file is `app.py` with variable `app`). |
| 500 error on site | Logs on Render; usually `DATABASE_URL` wrong or Supabase not allowing connections. In Supabase, check **Settings → Database** and that the connection string and password are correct. |
| Admin login not working | Ensure `SUPERADMIN_EMAIL` in Render matches the email of a user in your `users` table who is also in the `admin` table (or your app’s superadmin logic). |

You’re done. Your app is live.
