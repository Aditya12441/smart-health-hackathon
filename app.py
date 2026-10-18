"""Smart Health hackathon prototype. Uses demo data only."""
import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "local-demo-only-change-me"),
    MAX_CONTENT_LENGTH=16 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

# Demo-only in-memory data; resets when the process restarts.
# Do not enter real patient or sensitive health information.
patients = [
    {"id": 1, "name": "Aarav Sharma", "age": 28, "condition": "Routine check-up"},
    {"id": 2, "name": "Meera Patel", "age": 42, "condition": "Follow-up"},
]
appointments = [
    {"id": 1, "patient": "Aarav Sharma", "doctor": "Dr. Rao", "date": date.today().isoformat(), "time": "10:30", "status": "Scheduled"},
    {"id": 2, "patient": "Meera Patel", "doctor": "Dr. Khan", "date": date.today().isoformat(), "time": "12:00", "status": "Waiting"},
]
inventory = [
    {"id": 1, "name": "Paracetamol 500 mg", "category": "Pain relief", "stock": 120, "minimum": 40, "unit": "tablets"},
    {"id": 2, "name": "ORS Sachets", "category": "Rehydration", "stock": 18, "minimum": 30, "unit": "sachets"},
    {"id": 3, "name": "Disposable Gloves", "category": "PPE", "stock": 75, "minimum": 25, "unit": "pairs"},
    {"id": 4, "name": "Surgical Masks", "category": "PPE", "stock": 12, "minimum": 50, "unit": "pieces"},
]

def valid_text(value, max_length=100):
    return isinstance(value, str) and 0 < len(value.strip()) <= max_length and not any(ord(c) < 32 for c in value)

def parse_int(value, maximum=1_000_000):
    try:
        if not isinstance(value, str) or not value.strip():
            return None
        number = int(value)
        return number if 0 <= number <= maximum else None
    except (TypeError, ValueError):
        return None

def next_id(records):
    return max((record.get("id", 0) for record in records), default=0) + 1

def get_stats():
    return {
        "patients": len(patients),
        "appointments": len(appointments),
        "inventory_items": len(inventory),
        "low_stock": sum(item["stock"] < item["minimum"] for item in inventory),
    }

@app.after_request
def security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store")
    return response

@app.route("/")
def dashboard():
    low_stock_items = [item for item in inventory if item["stock"] < item["minimum"]]
    return render_template("index.html", stats=get_stats(), patients=patients,
                           appointments=appointments, inventory=inventory,
                           low_stock_items=low_stock_items, active="dashboard")

@app.route("/patients", methods=["GET", "POST"])
def patient_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = parse_int(request.form.get("age", ""), maximum=120)
        condition = request.form.get("condition", "Routine check-up").strip() or "Not specified"
        if not valid_text(name, 100) or age is None or age < 1:
            flash("Enter a valid name and an age between 1 and 120.", "error")
        elif not valid_text(condition, 120):
            flash("Visit type must be 120 characters or fewer.", "error")
        else:
            patients.append({"id": next_id(patients), "name": name, "age": age, "condition": condition})
            flash("Demo patient added successfully.", "success")
            return redirect(url_for("patient_page"))
    return render_template("patients.html", patients=patients, active="patients")

@app.route("/appointments", methods=["GET", "POST"])
def appointment_page():
    if request.method == "POST":
        patient = request.form.get("patient", "").strip()
        doctor = request.form.get("doctor", "").strip()
        date_raw = request.form.get("date", "").strip()
        time_raw = request.form.get("time", "").strip()
        try:
            appt_date = date.fromisoformat(date_raw)
            appt_time = datetime.strptime(time_raw, "%H:%M").time()
        except (TypeError, ValueError):
            appt_date, appt_time = None, None
        patient_names = {p["name"] for p in patients}
        if patient not in patient_names:
            flash("Choose a registered demo patient.", "error")
        elif not valid_text(doctor, 100):
            flash("Enter a valid doctor name.", "error")
        elif appt_date is None or appt_time is None:
            flash("Enter a valid appointment date and time.", "error")
        elif appt_date < date.today():
            flash("Appointment date cannot be in the past.", "error")
        else:
            appointments.append({"id": next_id(appointments), "patient": patient, "doctor": doctor,
                                 "date": appt_date.isoformat(), "time": appt_time.strftime("%H:%M"),
                                 "status": "Scheduled"})
            flash("Demo appointment added.", "success")
            return redirect(url_for("appointment_page"))
    return render_template("appointments.html", appointments=appointments, patients=patients, active="appointments")

@app.route("/inventory", methods=["GET", "POST"])
def inventory_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        stock = parse_int(request.form.get("stock", ""))
        minimum = parse_int(request.form.get("minimum", ""))
        unit = request.form.get("unit", "units").strip() or "units"
        if not valid_text(name, 100) or not valid_text(category, 80):
            flash("Enter a valid item name and category.", "error")
        elif stock is None or minimum is None:
            flash("Stock and minimum must be whole numbers from 0 to 1,000,000.", "error")
        elif not valid_text(unit, 30):
            flash("Unit must be 30 characters or fewer.", "error")
        else:
            inventory.append({"id": next_id(inventory), "name": name, "category": category,
                              "stock": stock, "minimum": minimum, "unit": unit})
            flash("Inventory item added.", "success")
            return redirect(url_for("inventory_page"))
    return render_template("inventory.html", inventory=inventory, active="inventory")

@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    answer, question = None, ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if not question or len(question) > 1000:
            answer = "Enter a question of 1–1000 characters."
        else:
            q = question.casefold()
            emergency = ("emergency", "chest pain", "can't breathe", "cannot breathe",
                         "difficulty breathing", "unconscious", "stroke", "severe bleeding")
            if any(term in q for term in emergency):
                answer = "This may be an emergency. Contact local emergency services immediately (112 in India) or go to the nearest emergency department. Do not rely on this demo assistant."
            elif any(term in q for term in ("stock", "medicine", "supply", "inventory", "shortage")):
                low = [i for i in inventory if i["stock"] < i["minimum"]]
                summary = ", ".join(f'{i["name"]} ({i["stock"]} {i["unit"]}; minimum {i["minimum"]})' for i in low)
                answer = "Inventory summary: " + (summary or "No items are below their minimum stock level.") + " Confirm quantities and expiry dates with authorized staff."
            elif any(term in q for term in ("appointment", "doctor", "schedule")):
                answer = f"There are {len(appointments)} demo appointments recorded. Confirm schedules with the clinic team."
            else:
                answer = "This demo cannot diagnose or prescribe. For personal symptoms or treatment decisions, contact a qualified healthcare professional. For urgent or severe symptoms, seek emergency care."
    return render_template("assistant.html", answer=answer, question=question, active="assistant")

@app.route("/health")
def health():
    return jsonify(status="ok", app="Smart Health", timestamp=datetime.now().astimezone().isoformat())

@app.errorhandler(413)
def request_too_large(_error):
    return jsonify(error="Request body too large."), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=False)
