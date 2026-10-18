# Smart Health — AI-Driven Health Center & Supply Chain Management

A responsive hackathon prototype that brings basic clinic operations and medical-supply visibility into one dashboard.

## Features
- Overview dashboard for patients, appointments, inventory and low-stock alerts.
- Add fictional patient records and appointments.
- Add supply items and automatically flag stock below a configurable minimum.
- Rule-based assistant for inventory and operational summaries, with emergency guidance and clear medical limitations.
- Responsive interface and a `/health` endpoint for basic health checks.
- Dockerfile included for deployment to Google Cloud Run.

## Run locally
Requires Python 3.10 or later.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8080

## Deploy to Google Cloud Run
1. Create a public GitHub repository and upload these files.
2. In Google Cloud Console, create/select a project and enable billing if required.
3. Open Cloud Run and choose **Deploy a container** / deploy from source (the console labels can change).
4. Connect the GitHub repository or use the source deployment flow; build from the included Dockerfile.
5. Allow unauthenticated access only if your hackathon demo needs to be publicly viewable. Copy the resulting HTTPS URL and test it in a private/incognito window.

Alternative with Google Cloud CLI after installing and authenticating `gcloud`:

```bash
gcloud run deploy smart-health --source . --region asia-south1 --allow-unauthenticated
```

## Important prototype limitations
- All records are fictional demo data held in process memory; they reset when the app restarts and are not shared across instances.
- This is not production-ready and must not store real patient data. Add authentication, authorization, a secure database, audit logs, encryption, validation and privacy/security review before any real use.
- The assistant is rule-based, not a connected large language model. It is not a medical device and does not diagnose, prescribe or replace a qualified clinician.
- Use the official emergency number applicable to the deployment location. This demo mentions 112 for India.

## Suggested hackathon demo
1. Show the dashboard and its low-stock alerts.
2. Add a fictional patient and an appointment.
3. Add a supply item with stock below minimum and show the alert.
4. Ask the assistant which supplies are low.
5. Explain how real deployments could add supplier lead times, expiry tracking, demand forecasting and authenticated access.

## Tech stack
Python · Flask · HTML · CSS · Docker · Google Cloud Run
