"""Smart Health demo application.

All records are in-memory demo data. Never enter real patient information.
"""
import os
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or "local-demo-only-change-me",
    MAX_CONTENT_LENGTH=16 * 1024,  # small form submissions only
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Enable only when the deployment is served exclusively over HTTPS.
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

# Demo-only in-memory data. This resets when the process restarts.
# Do not use real patient information or deploy this prototype for clinical use.
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


@app.after_request
def add_security_headers(response):
    """Set low-risk browser security headers for all responses."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


def next_id(records):
    """Return the next ID without assuming records are non-empty."""
    return max((record.get("id", 0) for record in records), default=0) + 1


def valid_text(value, *, max_length=100):
    """Accept non-empty, bounded text and reject control characters."""
    if not isinstance(value, str):
        return False
    value = value.strip()
    return bool(value) and len(value) <= max_length and not any(ord(ch) < 32 and ch not in "\t" for ch in value)


def parse_nonnegative_int(value, *, maximum=1_000_000):
    """Parse a bounded non-negative integer; return None for invalid values."""
    try:
        if not isinstance(value, str) or not value.strip():
            return None
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 0 <= number <= maximum else None


def get_stats():
    return {
        "patients": len(patients),
        "appointments": len(appointments),
        "inventory_items": len(inventory),
        "low_stock": sum(item["stock"] < item["minimum"] for item in inventory),
    }


@app.route("/")
def dashboard():
    low_stock_items = [item for item in inventory if item["stock"] < item["minimum"]]
    return render_template(
        "index.html", stats=get_stats(), patients=patients,
        appointments=appointments, inventory=inventory,
        low_stock_items=low_stock_items, active="dashboard",
    )


@app.route("/patients", methods=["GET", "POST"])
def patient_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age_raw = request.form.get("age", "").strip()
        condition = request.form.get("condition", "Routine check-up").strip() or "Not specified"
        age = parse_nonnegative_int(age_raw, maximum=120)
        if not valid_text(name, max_length=100) or age is None or age < 1:
            flash("Enter a valid name (up to 100 characters) and an age between 1 and 120.", "error")
        elif not valid_text(condition, max_length=120):
            flash("Visit type must be 120 characters or fewer.", "error")
        else:
            patients.append({
                "id": next_id(patients), "name": name, "age": age, "condition": condition,
            })
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

        # Validate actual date/time values, not just non-empty strings.
        try:
            appointment_date = date.fromisoformat(date_raw)
            appointment_time = datetime.strptime(time_raw, "%H:%M").time()
            valid_datetime = True
        except (TypeError, ValueError):
            valid_datetime = False

        known_patient_names = {p["name"] for p in patients}
        if not valid_text(patient, max_length=100) or patient not in known_patient_names:
            flash("Choose a patient from the registered patient list.", "error")
        elif not valid_text(doctor, max_length=100):
            flash("Enter a valid doctor name (up to 100 characters).", "error")
        elif not valid_datetime:
            flash("Enter a valid appointment date and time.", "error")
        elif appointment_date < date.today():
            flash("Appointment date cannot be in the past.", "error")
        else:
            appointments.append({
                "id": next_id(appointments), "patient": patient, "doctor": doctor,
                "date": appointment_date.isoformat(), "time": appointment_time.strftime("%H:%M"),
                "status": "Scheduled",
            })
            flash("Demo appointment added.", "success")
            return redirect(url_for("appointment_page"))
    return render_template(
        "appointments.html", appointments=appointments, patients=patients, active="appointments"
    )


@app.route("/inventory", methods=["GET", "POST"])
def inventory_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        stock = parse_nonnegative_int(request.form.get("stock", ""))
        minimum = parse_nonnegative_int(request.form.get("minimum", ""))
        unit = request.form.get("unit", "units").strip() or "units"

        if not valid_text(name, max_length=100) or not valid_text(category, max_length=80):
            flash("Enter a valid item name and category.", "error")
        elif stock is None or minimum is None:
            flash("Stock and minimum level must be whole numbers from 0 to 1,000,000.", "error")
        elif not valid_text(unit, max_length=30):
            flash("Unit must be 30 characters or fewer.", "error")
        else:
            inventory.append({
                "id": next_id(inventory), "name": name, "category": category,
                "stock": stock, "minimum": minimum, "unit": unit,
            })
            flash("Inventory item added.", "success")
            return redirect(url_for("inventory_page"))
    return render_template("inventory.html", inventory=inventory, active="inventory")


@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    answer = None
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if not question or len(question) > 1000:
            answer = "Enter a question of 1–1000 characters."
        else:
            q = question.casefold()
            emergency_terms = (
                "emergency", "chest pain", "can't breathe", "cannot breathe",
                "difficulty breathing", "unconscious", "stroke", "severe bleeding",
            )
            if any(term in q for term in emergency_terms):
                answer = (
                    "This may be an emergency. Contact local emergency services immediately "
                    "(112 in India) or go to the nearest emergency department. Do not rely on this demo assistant."
                )
            elif any(word in q for word in ("stock", "medicine", "supply", "inventory", "shortage")):
                low = [item for item in inventory if item["stock"] < item["minimum"]]
                summary = ", ".join(
                    f'{item["name"]} ({item["stock"]} {item["unit"]}; minimum {item["minimum"]})'
                    for item in low
                )
                answer = "Inventory summary: " + (
                    summary if summary else "No items are currently below their minimum stock level."
                ) + " Confirm quantities and expiry dates with authorized staff before ordering."
            elif any(word in q for word in ("appointment", "doctor", "schedule")):
                answer = (
                    f"There are {len(appointments)} demo appointments recorded. "
                    "Please confirm schedules directly with the clinic team."
                )
            else:
                answer = (
                    "I cannot diagnose, prescribe, or replace a licensed clinician. "
                    "For personal symptoms or treatment decisions, contact a qualified healthcare professional. "
                    "For urgent or severe symptoms, seek emergency care."
                )
    return render_template("assistant.html", answer=answer, question=question, active="assistant")


@app.route("/health")
def health():
    """Lightweight readiness endpoint for hosting platforms and monitoring."""
    return jsonify(status="ok", app="Smart Health", timestamp=datetime.now().astimezone().isoformat())


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify(error="Request body too large."), 413


@app.errorhandler(500)
def internal_error(_error):
    # Do not expose exception details or configuration to visitors.
    app.logger.exception("Unhandled application error")
    return render_template(
        "base.html",
        title="Server error",
        heading="Something went wrong",
        active="",
    ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=False)
