# Smart Health Hackathon Prototype

A Flask demo with a dashboard, patient records, appointment scheduling, inventory low-stock alerts, and a rule-based assistant.

## Run locally
Requires Python 3.11+.
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000.

## Automated tests
```bash
python -m unittest discover -s tests -v
```

## Deploy
This repository includes a Dockerfile and Render configuration. Connect the repository in Render and deploy the web service.

## Limitations
Demo data is stored in memory and resets on restart. No authentication or database is included. Do not enter real patient information. The assistant does not diagnose or prescribe.
