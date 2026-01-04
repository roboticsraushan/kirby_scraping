# Kirby Scraping — Run & Setup ✅

## Overview 🔧
Small Flask app for scraping and sending emails. This README explains how to set up a local development environment using a Python virtual environment and how to run the app.

---

## Prerequisites ⚙️
- Python 3.10+ (3.12 recommended)
- `python3-venv` (Debian/Ubuntu): `sudo apt install python3-venv`
- Git (optional)

---

## Quick start (recommended: virtualenv) 🐍
1. Open a terminal in the project root (where `app.py` and `requirements.txt` live).

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> If `python3 -m venv` fails, install the system package: `sudo apt install python3-venv`.

3. Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Create an environment file `.env` (the app uses python-dotenv to load env vars). Example values are below — do **not** commit real secrets to git.

```bash
cat > .env <<'EOF'
SECRET_KEY=change-me
SENDER_EMAIL=hello@example.com
SENDER_NAME=Your Name
GMAIL_APP_PASSWORD=your_gmail_app_password
TEST_EMAIL=you@example.com
FLASK_ENV=development
EOF
```

5. Run the app:

```bash
python app.py
# or, explicitly from the venv
.venv/bin/python app.py
```

The server will be available at `http://127.0.0.1:5000` (and on your LAN IP if applicable).

---

## Useful commands 🧰
- Stop server: `Ctrl+C`
- Reinstall dependencies after changing `requirements.txt`:
  - `pip install -r requirements.txt`
- Run an endpoint quickly with curl:
  - `curl http://127.0.0.1:5000/`

---

## Troubleshooting ⚠️
- `venv` creation fails with `ensurepip` errors → run `sudo apt install python3-venv`.
- `pip install` blocked with "externally-managed environment" → ensure you're inside the virtualenv and run `pip` there.
- Missing modules after activation → double-check that `.venv` is active (`which python` should point to `.venv/bin/python`).

---

## Next steps & notes ✅
- If you'd like, I can add a `.env.example` file with safe example values and add a short "Run" section to a `CONTRIBUTING.md` or expand this README.
- For any email-sending tests, set `GMAIL_APP_PASSWORD` with an app-specific password or use test/mock SMTP settings.

---

If you'd like me to create `.env.example` and/or add a small run section to a `README.md` in a slightly different format (shorter or more verbose), reply and I'll add it. ✨
