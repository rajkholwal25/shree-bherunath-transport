# Commit to GitHub and Update Render

## 1. Commit and push to GitHub

Open **Git Bash** or **PowerShell** (in the project folder) and run:

```bash
cd C:\Users\Mohit.m\Downloads\bhopu

git add .
git status
git commit -m "Update: mobile UI, forgot password email, contact number +91 93289 28101, driver dropdown"
git push origin main
```

- If you use a different branch name (e.g. `master`), use that instead of `main`.
- If Git asks for username/password, use your **GitHub username** and a **Personal Access Token** (not your GitHub password).

---

## 2. Update Render (after push)

Render **auto-deploys** when you push to the connected branch (usually `main`). So after `git push`:

1. Go to **[render.com](https://render.com)** → **Dashboard** → your service **shree-bherunath-transport**.
2. You should see a new **Deploy** start (or go to **Events** / **Logs** to confirm).
3. Wait 2–3 minutes for the build to finish. Your live site will then have the latest code.

### Optional: Add env vars on Render (for password reset email)

If you want “Forgot password?” to **send the reset link by email** on the live site, add these in Render:

1. Your service → **Environment** (left sidebar).
2. **Add Environment Variable**:
   - **Key:** `RESEND_API_KEY`  
     **Value:** your Resend API key (e.g. `re_BYxStTVZ_...`).
   - **Key:** `RESEND_FROM`  
     **Value:** `Shree Bherunath Transport <onboarding@resend.dev>`
3. **Save**. Render will redeploy once. After that, reset emails will work in production too.

---

## Quick checklist

| Step | Action |
|------|--------|
| 1 | `git add .` then `git commit -m "..."` then `git push origin main` |
| 2 | Open Render dashboard; wait for auto-deploy to finish |
| 3 | (Optional) Add `RESEND_API_KEY` and `RESEND_FROM` in Render Environment if you want email reset on live site |

Done. Your updates (mobile UI, forgot password, new contact number, etc.) will be on GitHub and on Render after the deploy completes.
