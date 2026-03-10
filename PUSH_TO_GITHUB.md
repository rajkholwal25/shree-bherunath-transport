# Push Shree Bherunath Transport to GitHub – Step by Step

Follow these steps in order. Use **Command Prompt** or **PowerShell** (or Terminal on Mac/Linux).

---

## Step 1: Install Git (if you don’t have it)

1. Check if Git is installed:
   ```bash
   git --version
   ```
2. If you see a version (e.g. `git version 2.43.0`), skip to Step 2.
3. If you see “command not found” or an error:
   - Download: https://git-scm.com/download/win
   - Run the installer (default options are fine).
   - Close and reopen your terminal, then run `git --version` again.

---

## Step 2: Create a GitHub account (if you don’t have one)

1. Go to https://github.com
2. Click **Sign up** and create an account (email, password, username).
3. Verify your email if asked.

---

## Step 3: Open your project folder in the terminal

1. Open **Command Prompt** or **PowerShell**.
2. Go to your project folder. For example, if the project is in `Downloads\bhopu`:
   ```bash
   cd C:\Users\Mohit.m\Downloads\bhopu
   ```
   (Replace with your actual path if different.)
3. Confirm you’re in the right place:
   ```bash
   dir
   ```
   You should see folders like `templates`, `static`, `models` and files like `app.py`, `requirements.txt`.

---

## Step 4: Create a .gitignore (so secrets and junk don’t go to GitHub)

1. In your project folder, create a file named **`.gitignore`** (with the dot at the start).
2. Put this inside it (you can use Notepad or VS Code):

   ```
   .env
   __pycache__/
   *.pyc
   .venv/
   venv/
   *.egg-info/
   .idea/
   .vscode/
   *.log
   ```

3. Save the file in the root of the project (same place as `app.py`).  
   This keeps your `.env` (passwords, keys) and Python cache out of GitHub.

---

## Step 5: Initialize Git in your project

In the same terminal (still in your project folder):

```bash
git init
```

You should see: `Initialized empty Git repository in .../bhopu/.git/`

---

## Step 6: Tell Git who you are (one-time per computer)

Use the **same email** you used for GitHub:

```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

Example:

```bash
git config --global user.email "rajkholwal25.2@gmail.com"
git config --global user.name "Mohit"
```

---

## Step 7: Add all project files

```bash
git add .
```

This stages everything. The `.gitignore` will still prevent `.env` and the other listed items from being added.

---

## Step 8: First commit

```bash
git commit -m "Initial commit - Shree Bherunath Transport"
```

You should see a message like: `X files changed, Y insertions(+)`.

---

## Step 9: Create a new repository on GitHub

1. Go to https://github.com and log in.
2. Click the **+** (top right) → **New repository**.
3. Fill in:
   - **Repository name:** e.g. `bhopu` or `shree-bherunath-transport`
   - **Description:** (optional) e.g. `Truck transport booking – Flask + Supabase`
   - **Public**
   - **Do not** check “Add a README” or “Add .gitignore” (you already have code).
4. Click **Create repository**.

---

## Step 10: Connect your folder to GitHub and push

GitHub will show a page with commands. Use these (replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name):

**Example:** if your username is `mohitmeena` and repo name is `bhopu`:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

Example:

```bash
git remote add origin https://github.com/mohitmeena/bhopu.git
```

Then:

```bash
git branch -M main
git push -u origin main
```

- If GitHub asks for login, use your **GitHub username** and a **Personal Access Token** (not your normal password).  
  To create a token: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Generate new token**; give it “repo” scope and use it when Git asks for password.
- After a successful push, refresh your repo page on GitHub; you’ll see all your files there.

---

## Step 11: Later – when you change code and want to update GitHub

Whenever you change something and want to save it on GitHub:

```bash
cd C:\Users\Mohit.m\Downloads\bhopu
git add .
git commit -m "Short description of what you changed"
git push
```

Example:

```bash
git add .
git commit -m "Updated navbar and footer text"
git push
```

---

## Quick copy-paste summary (after Step 3)

```bash
cd C:\Users\Mohit.m\Downloads\bhopu
git init
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
git add .
git commit -m "Initial commit - Shree Bherunath Transport"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

Replace `your-email@example.com`, `Your Name`, `YOUR_USERNAME`, and `YOUR_REPO` with your details. Create the repo on GitHub (Step 9) **before** running the `git remote` and `git push` commands.

---

## If something goes wrong

- **“fatal: not a git repository”**  
  Run `git init` inside your project folder (Step 5).

- **“Permission denied” or “Authentication failed”**  
  Use a **Personal Access Token** instead of password: GitHub → Settings → Developer settings → Personal access tokens → Generate; use the token when Git asks for password.

- **“Updates were rejected”**  
  If the GitHub repo had a README or other file created on the site, run once:  
  `git pull origin main --allow-unrelated-histories`  
  then fix any conflicts if asked, and run `git push` again.

- **Wrong files added (e.g. .env)**  
  Add `.env` to `.gitignore`, then run:  
  `git rm --cached .env`  
  and commit again. Never push `.env` if it contains real passwords or keys.
