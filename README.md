# Smart Health — Healthcare Center & Supply Chain Prototype

A Flask hackathon prototype with a dashboard, demo patient records, appointment scheduling, medicine/supply inventory, low-stock alerts, and a rule-based operational assistant.

## Features
- Dashboard summary metrics and low-stock inventory list
- Input validation for patient, appointment, and inventory forms
- Rejects unknown patients and past appointment dates
- Rule-based assistant for stock/appointment summaries and emergency escalation messaging
- `/health` JSON health-check endpoint
- Basic browser security headers and request-size limit
- Automated unit tests and GitHub Actions workflow with coverage reporting
- Render and Docker deployment files

## Run locally
Python 3.11 recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8080.

## Run tests
```bash
pip install -r requirements.txt
pip install coverage
coverage run -m unittest discover -s tests -v
coverage report -m
```

## Deploy on Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Set `SECRET_KEY` to a long random secret in Render environment settings.
- The included `render.yaml` also configures a generated secret.

## Important limitations
This is a demonstration prototype. Data is stored in memory and resets on restart. It has no authentication, database persistence, or role-based access. Do not enter real patient data. The assistant is rule-based, not a medical diagnostic tool. Production use requires a security/privacy review, authentication, persistent storage, audit logs, CSRF protection, and clinical validation.
