# Push to GitHub – Every Step Explained (rajkholwal25@gmail.com)

This guide explains **what each step does** and **what to type**, using your email **rajkholwal25@gmail.com**.

---

## Before you start

- You need: **Git** installed, **GitHub account** (rajkholwal25@gmail.com), and your project folder **bhopu**.
- Use **Git Bash** (MINGW64) or **Command Prompt** or **PowerShell**.

---

## STEP 1: Open the terminal in your project folder

**What we’re doing:** So that all commands run inside your **bhopu** project.

**Type:**
```bash
cd C:/Users/Mohit.m/Downloads/bhopu
```

**Explanation:**  
`cd` = “change directory”. This moves you into the folder where `app.py`, `templates`, `static`, etc. are.  
If your project is somewhere else (e.g. Desktop), use that path instead.

**Check:** Run `ls` (Git Bash) or `dir` (CMD). You should see `app.py`, `templates`, `static`, `requirements.txt`, etc.

---

## STEP 2: Set your Git name and email (one-time on this PC)

**What we’re doing:** Telling Git who is making the commits. GitHub will show this name and email on every commit.

**Type these two lines (use your real name if you prefer):**
```bash
git config --global user.email "rajkholwal25@gmail.com"
git config --global user.name "Raj Kholwal"
```

**Explanation:**  
- `user.email` = the email of your **GitHub account** (rajkholwal25@gmail.com).  
- `user.name` = the name that will appear on commits; you can use "Raj Kholwal" or any name you like.  
- `--global` = use this for all repos on this computer (you only set it once).

---

## STEP 3: Turn your folder into a Git repository

**What we’re doing:** Creating a hidden `.git` folder so Git can track every file and change.

**Type:**
```bash
git init
```

**Explanation:**  
`init` = initialize. After this, Git will track changes in this folder. You should see:  
`Initialized empty Git repository in .../bhopu/.git/`

---

## STEP 4: See what Git will add (optional)

**What we’re doing:** Checking which files will be included. Your `.env` should **not** appear (it’s in `.gitignore`).

**Type:**
```bash
git status
```

**Explanation:**  
You’ll see a list of files in red (untracked). Those are the files that will be added in the next step.  
If `.env` appears, **do not continue** until you’ve added `.env` to `.gitignore` (it should already be there).

---

## STEP 5: Stage all files for the first commit

**What we’re doing:** Telling Git “include all these files in the next save (commit)”. Files in `.gitignore` (like `.env`) are still ignored.

**Type:**
```bash
git add .
```

**Explanation:**  
`add` = stage. The dot (`.`) means “current folder and everything inside it”.  
Nothing will seem to happen; the next step actually saves.

---

## STEP 6: Save the first version (first commit)

**What we’re doing:** Creating the first “save point” of your project with a short message.

**Type:**
```bash
git commit -m "Initial commit - Shree Bherunath Transport"
```

**Explanation:**  
`commit` = save this snapshot.  
`-m "..."` = message that describes what this save is. You’ll see something like:  
`X files changed, Y insertions(+)`.  
That’s your first commit. It exists only on your PC until you push.

---

## STEP 7: Create a new empty repository on GitHub

**What we’re doing:** Creating the “place” on GitHub where your code will live. We do this in the browser, not in the terminal.

1. Open: **https://github.com** and log in with **rajkholwal25@gmail.com** (or the account you use for GitHub).
2. Click the **+** (top right) → **New repository**.
3. Fill the form:
   - **Repository name:** e.g. `bhopu` or `shree-bherunath-transport` (no spaces).
   - **Description (optional):** e.g. `Truck transport booking - Flask + Supabase`.
   - Choose **Public**.
   - **Do not** tick “Add a README file” or “Add .gitignore” (we already have code).
4. Click **Create repository**.

**Explanation:**  
GitHub will show a page with commands. We’ll use the “push an existing repository” part in the next steps.  
Your repo URL will look like: `https://github.com/YOUR_USERNAME/bhopu` (replace YOUR_USERNAME with your GitHub username).

---

## STEP 8: Connect your PC folder to the GitHub repo

**What we’re doing:** Linking your local folder to the repo you just created. Replace **YOUR_GITHUB_USERNAME** with your actual GitHub username (e.g. if your profile is github.com/rajkholwal, use `rajkholwal`).

**Type (replace YOUR_GITHUB_USERNAME and REPO_NAME):**
```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/REPO_NAME.git
```

**Example** (if username is `rajkholwal` and repo name is `bhopu`):
```bash
git remote add origin https://github.com/rajkholwal/bhopu.git
```

**Explanation:**  
`remote` = a place on the internet (GitHub).  
`origin` = the default name for that place.  
So we’re saying: “The GitHub repo at this URL is my ‘origin’.”  
If you get “remote origin already exists”, run: `git remote remove origin` then run the `git remote add` line again.

---

## STEP 9: Name your main branch “main”

**What we’re doing:** Making sure your main branch is called `main` (GitHub’s default).

**Type:**
```bash
git branch -M main
```

**Explanation:**  
`branch -M main` = rename the current branch to `main`.  
Your first commit is on this branch; we’ll push it in the next step.

---

## STEP 10: Push your code to GitHub

**What we’re doing:** Uploading all your commits (so far, the first one) to GitHub.

**Type:**
```bash
git push -u origin main
```

**Explanation:**  
`push` = send my commits to the remote.  
`origin` = the GitHub repo we added in Step 8.  
`main` = the branch we’re pushing.  
`-u` = remember this link so next time you can just type `git push`.

**If Git asks for username and password:**  
- **Username:** your **GitHub username** (not the email).  
- **Password:** use a **Personal Access Token**, not your GitHub password.  
  - Create one: GitHub → your profile (top right) → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**.  
  - Give it a name (e.g. “bhopu push”), tick **repo**, generate, then **copy the token** and paste it when Git asks for password.

After it finishes, refresh your repo page on GitHub; you should see all your files.

---

## What to do later when you change code

Every time you change something and want to update GitHub:

1. Open terminal and go to the project:
   ```bash
   cd C:/Users/Mohit.m/Downloads/bhopu
   ```
2. Stage changes:
   ```bash
   git add .
   ```
3. Commit with a short message:
   ```bash
   git commit -m "What you changed, e.g. Updated navbar"
   ```
4. Push to GitHub:
   ```bash
   git push
   ```

---

## Quick checklist (your email: rajkholwal25@gmail.com)

| Step | Command / Action |
|------|-------------------|
| 1 | `cd C:/Users/Mohit.m/Downloads/bhopu` |
| 2 | `git config --global user.email "rajkholwal25@gmail.com"` |
| 2 | `git config --global user.name "Raj Kholwal"` |
| 3 | `git init` |
| 4 | `git status` (optional) |
| 5 | `git add .` |
| 6 | `git commit -m "Initial commit - Shree Bherunath Transport"` |
| 7 | On GitHub: New repository (e.g. name: `bhopu`), don’t add README |
| 8 | `git remote add origin https://github.com/YOUR_USERNAME/bhopu.git` |
| 9 | `git branch -M main` |
| 10 | `git push -u origin main` (use token as password if asked) |

Replace **YOUR_USERNAME** with your GitHub username (the one in your profile URL).
