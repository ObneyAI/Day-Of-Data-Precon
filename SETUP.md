# Workshop Setup — *AI for the Rest of Us*
### Day of Data BR Pre-Con · Friday, July 17 · 8:00am–4:00pm (please arrive 7:30 for security)
### Blue Cross Blue Shield, Bluebonnet — Customer Service Building, Rooms 2A & 2B

Welcome! Please set up your laptop **before Friday** so we spend the day building, not installing.
**This guide assumes zero coding experience** — every step tells you exactly what to click and how to check it worked.

- ⏱️ **Time:** about **45–60 minutes**, mostly downloads. Do it on **home/office Wi-Fi** — a couple of downloads are 1–2 GB.
- 💻 **Laptop:** **Windows 11**, or a **Mac with Apple Silicon (M1/M2/M3/M4)** — one you're allowed to install software on.
- 🆘 **Stuck on any step? That's normal.** Do what you can, note where it stopped, and **reply to this email with a
  screenshot** — we'll help, and there's a no-Docker backup so **you'll be able to do everything on Friday regardless.**
- 📦 **The workshop files** (notebooks + setup scripts) live in a public GitHub repo — you'll grab them with one command
  Friday morning (see step 9), or early if you like. Today is mainly installing the tools.
- 🌐 **A Chrome or Edge browser** — one afternoon exercise loads a browser extension, which Safari can't do. Most laptops
  already have one; Safari-only Mac users, grab **Chrome** (google.com/chrome).

---

## First: how to open a "Terminal" (you'll use it a few times)
A **Terminal** is a window where you type commands. Opening it is the only "coding-ish" thing you need to know.

- **Windows:** click **Start**, type **`PowerShell`**, click **Windows PowerShell**. *(Blue window.)*
- **Mac:** press **⌘ (Command) + Space**, type **`Terminal`**, press **Enter**. *(Black/white window.)*

When a step says "run this," you **copy the line, paste it into that window, and press Enter.** That's it.

---

## Part 0 — Create your Claude Pro account *(the one paid item)*
**What it is:** the AI account that powers the two Claude apps we use all day.
**How:**
1. Go to **https://claude.ai/upgrade**
2. Sign in (or create a free account), then choose **Claude Pro** — about **$20/month, cancel anytime after the workshop**.

*(We need Pro because "Claude Code," which we build with, is included in it.)*

---

## Part 1 — Install the tools (in this order)

### 1) Docker Desktop  — *runs the workshop database on your laptop*
- **Get it:** **https://www.docker.com/products/docker-desktop/** → click the download for your system (Windows, or **Mac – Apple Silicon**).
- **Install it:**
  - **Windows:** run the downloaded installer, keep the default options (it will set up something called "WSL 2" for
    you — say yes), and **restart your PC** if it asks. Then open **Docker Desktop** from the Start menu and let it finish starting (whale icon in the taskbar).
    *(If it complains about "virtualization," reply to the email — it's a 1-line BIOS setting and we'll walk you through it.)*
  - **Mac:** open the downloaded `.dmg`, drag **Docker** to Applications, open it. Then — important — go to
    **Docker → Settings (gear) → General**, tick **"Use Rosetta for x86_64/amd64 emulation on Apple Silicon,"** click **Apply & Restart.**
- **Check it worked:** open a **Terminal** (see above) and run:
  ```
  docker --version
  ```
  You should see a version number (e.g. `Docker version 28.x`).

### 2) SQL Server 2025  — *the database itself (runs inside Docker)*
**With Docker Desktop open and running,** paste these into your Terminal, one at a time, pressing Enter after each.
- Download the database software (this is the ~1.5 GB one — do it at home):
  ```
  docker pull mcr.microsoft.com/mssql/server:2025-latest
  ```
- Start it *(copy it exactly — the **single quotes** around the password matter on Mac; the `!` misbehaves inside double quotes)*:
  ```
  docker run -e "ACCEPT_EULA=Y" -e 'MSSQL_SA_PASSWORD=Workshop!2026Pass' -p 1433:1433 --name dod-sql -d mcr.microsoft.com/mssql/server:2025-latest
  ```
- **Check it worked:**
  ```
  docker ps
  ```
  You should see a line that mentions **`dod-sql`**. 🎉 *(That's a real database server running on your laptop.)*

### 3) Python  — *the language our examples are written in*
- **Get it:** **https://www.python.org/downloads/** → click the big **Download Python 3.12** button.
- **Install it:**
  - **Windows:** run the installer and — **very important** — tick **"Add python.exe to PATH"** at the bottom of the
    first screen, then click **Install Now**.
  - **Mac:** run the installer, keep clicking **Continue / Install**.
- **Check it worked:** open a **new** Terminal and run:
  ```
  python --version
  ```
  (On Mac, if that says "not found," try `python3 --version`.) You want to see `Python 3.11` or higher.

### 4) Node.js  — *needed by the Claude Code tool*
- **Get it:** **https://nodejs.org** → click the **LTS** (recommended) button and run the installer with default options.
- **Check it worked:** in a **new** Terminal:
  ```
  node --version
  ```
  You want `v20` or higher.

### 5) Claude Desktop  — *the app where you'll chat with the AI*
- **Get it:** **https://claude.ai/download** → download and install the app for your system, open it, and **sign in**
  with the Claude Pro account from Part 0.
- **Check it worked:** the app opens and you can type a message and get a reply.

### 6) Claude Code  — *lets you build things by describing them ("vibe coding")*
- **Install it:** in a Terminal, run:
  ```
  npm install -g @anthropic-ai/claude-code
  ```
  *(This uses Node from step 4. If you see a yellow "engine" warning, ignore it — it still works.)*
- **Turn it on:** run `claude` — the first time, choose **"Log in with your Claude account"** (your Pro plan). Then type `exit`.
- **Check it worked:**
  ```
  claude --version
  ```
  shows a version number. *(Official help, if curious: https://code.claude.com/docs)*

### 7) VS Code  — *a friendly text editor (optional but recommended)*
- **Get it:** **https://code.visualstudio.com/** → download, install, open once. That's all for now.

### 8) The workshop Python packages
1. Make a folder for the workshop (e.g. **Documents → `dod-workshop`**). In your Terminal, go into it:
   - **Windows:** `cd Documents\dod-workshop`   •   **Mac:** `cd Documents/dod-workshop`
   *(If the folder isn't there yet, create it in your file explorer first, then run the line above.)*
2. Create a clean workspace and turn it on:
   - **Windows:**
     ```
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **Mac:**
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   *(You'll see `(.venv)` appear at the start of the line — that means it's on.)*
3. Install the packages (one command; downloads a few hundred MB):
   ```
   pip install fastmcp mssql-python sentence-transformers staticvectors jupyter numpy plotly scikit-learn
   ```
4. Pre-download the two small AI models (so the room isn't downloading them Friday):
   ```
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); from staticvectors import StaticVectors; StaticVectors('neuml/word2vec'); print('models ready')"
   ```
   You should see **`models ready`**. *(A yellow "HF_TOKEN" / HuggingFace warning along the way is normal — ignore it.)*

### 9) Get the workshop files *(quick — you can also do this Friday morning with us)*
Everything we build from lives in one public repo: **github.com/ObneyAI/Day-Of-Data-Precon**. Grab it whichever way is easier:

- **With Git** — Mac usually has it; on **Windows** install it first from **https://git-scm.com/download/win** (default options). Then,
  in a Terminal inside your `dod-workshop` folder, run:
  ```
  git clone https://github.com/ObneyAI/Day-Of-Data-Precon.git
  ```
  That creates a **`Day-Of-Data-Precon`** folder holding the notebooks + database scripts.
- **No Git / prefer clicking** — open that repo page, click the green **`< > Code`** button → **Download ZIP**, and unzip it into your `dod-workshop` folder.

> You don't *have* to do this before Friday — we clone it together first thing in the morning. But you're welcome to grab it early and look around.

---

## Part 2 — The 2-minute "did it all work?" check
Open a Terminal, turn the workspace on again if needed (`.venv\Scripts\activate` on Windows / `source .venv/bin/activate`
on Mac), and run each line. You want the ✅ result.

| Run this | ✅ You should see |
|----------|------------------|
| `docker ps` | a line with **dod-sql** |
| `python --version`  *(or `python3 --version`)* | `Python 3.11`+ |
| `node --version` | `v20`+ |
| `claude --version` | a version number |
| `python -c "import fastmcp, mssql_python, sentence_transformers, staticvectors, plotly, sklearn; print('packages ok')"` | `packages ok` |
| Open **Claude Desktop** | it opens and you're **signed in** |

If every row checks out, you're 100% ready. If not, no stress — bring it Friday, come a few minutes early, and we'll sort it.

---

## If you get stuck
- **Reply to this email** with the step number and a screenshot — we'll get you going before Friday or at the door.
- **Arrive by 7:30am** Friday; we help with setup from 7:30–8:00.
- **A no-Docker backup exists** — even if the database step fights you, you'll do every exercise on Friday.

See you Friday — come curious! 🌟
*— Daryl Roberts, Head of AI, obney.ai*
