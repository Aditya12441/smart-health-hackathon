# Smart Health — AI-Driven Health Center & Supply Chain Management

A Flask-based hackathon prototype demonstrating a clinic dashboard, demo patient directory, appointment planner, medical supply inventory, low-stock monitoring, and a rule-based operational assistant.

> **Prototype and safety notice:** The app uses in-memory sample data. Do not enter real patient or other sensitive health information. It is not a medical device and must not be used for diagnosis, treatment, or real clinical operations.

## Features

- Dashboard metrics for demo patients, appointments, inventory, and low-stock items.
- Patient form validation with bounded inputs.
- Appointment validation for registered demo patients, valid date/time, and non-past dates.
- Inventory validation with non-negative, bounded stock quantities.
- Rule-based assistant for inventory/appointment summaries and emergency escalation messaging.
- `/health` JSON readiness endpoint.
- Security response headers, bounded request size, environment-based secret configuration.
- Automated tests for routes, validation, core workflows, and safety responses.
- GitHub Actions workflow runs tests on pushes and pull requests.
- Accessibility enhancements: skip link, visible keyboard focus, semantic main landmark, live status messages, and reduced-motion support.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8080`.

## Run tests

```bash
python -m unittest discover -s tests -v
# Optional coverage report (install requirements-dev.txt first):
coverage run -m unittest discover -s tests -v
coverage report -m
```

## Deploy on Render

Use the project directory containing `app.py` as the Root Directory.

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- Add an environment variable named `SECRET_KEY` with a long, random value.
- Set `COOKIE_SECURE=1` when serving the app exclusively over HTTPS.

## Limitations and next steps

- Current records are stored in memory and reset when the process restarts; use a database for persistence.
- This prototype has no authentication or role-based access. Do not use real patient data.
- The assistant is rule-based and does not call an AI model or provide medical advice.
- For production, add authentication/authorization, CSRF protection, database migrations, audit logging, backups, privacy review, and comprehensive security testing.
