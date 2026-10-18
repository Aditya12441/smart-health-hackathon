from datetime import date, datetime
from flask import Flask, request, redirect, url_for, flash, jsonify, render_template_string
import os, re

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "smart-health-demo-change-me")

patients = [
    {"id": 1, "name": "Aarav Sharma", "age": 34, "gender": "Male", "phone": "9000000001", "condition": "Routine check-up"},
    {"id": 2, "name": "Priya Verma", "age": 28, "gender": "Female", "phone": "9000000002", "condition": "Follow-up"},
]
appointments = [{"id": 1, "patient": "Aarav Sharma", "doctor": "Dr. Mehta", "date": date.today().isoformat(), "time": "11:00"}]
inventory = [
    {"id": 1, "name": "ORS Sachets", "category": "Essential supplies", "stock": 8, "minimum": 10, "unit": "sachets"},
    {"id": 2, "name": "Surgical Masks", "category": "PPE", "stock": 45, "minimum": 20, "unit": "pieces"},
    {"id": 3, "name": "Disposable Gloves", "category": "PPE", "stock": 12, "minimum": 25, "unit": "pairs"},
    {"id": 4, "name": "Bandages", "category": "First aid", "stock": 30, "minimum": 15, "unit": "rolls"},
]
STYLE = """*{box-sizing:border-box}body{margin:0;background:#f3f7fb;color:#172b4d;font:15px Arial,sans-serif}header{background:#102a43;color:white;padding:18px 5%;display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap}.brand{font-size:21px;font-weight:bold;color:white;text-decoration:none}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{color:#e4eef7;text-decoration:none;padding:9px 11px;border-radius:8px}nav a:hover,nav a.active{background:#254660}main{max-width:1120px;width:92%;margin:28px auto 50px}.hero{padding:30px;background:linear-gradient(120deg,#102a43,#087f8c);color:white;border-radius:18px;margin-bottom:18px}h1{font-size:clamp(28px,4vw,38px);margin:7px 0}h2{font-size:20px;margin:0 0 16px}.muted{color:#647d95}.hero .muted{color:#e0f1f4}.stats,.cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:16px 0}.cols{grid-template-columns:repeat(2,minmax(0,1fr))}.card{background:white;border:1px solid #d9e2ec;border-radius:14px;padding:22px;box-shadow:0 6px 22px #102a4310;min-width:0}.stat strong{display:block;font-size:30px;margin:8px 0}.stat a,.link{color:#087f8c;font-weight:bold;text-decoration:none}.btn,button{display:inline-block;background:#087f8c;color:white;border:0;border-radius:8px;padding:11px 15px;text-decoration:none;font-weight:bold;cursor:pointer}.btn:hover,button:hover{background:#066b75}label{display:block;font-size:13px;font-weight:bold;margin:12px 0 5px}input,select,textarea{width:100%;padding:11px;border:1px solid #cbd5e1;border-radius:8px;font:inherit;background:white}table{width:100%;border-collapse:collapse;margin-top:12px}th,td{text-align:left;padding:11px 8px;border-bottom:1px solid #edf2f7}th{font-size:11px;color:#627d98;text-transform:uppercase}small{display:block;color:#627d98;margin-top:4px}.pill{display:inline-block;background:#edf2f7;border-radius:20px;padding:4px 8px;font-size:11px}.low{background:#fff0ef;color:#b42318}.ok{background:#e9f9ef;color:#087443}.flash{padding:12px;border-radius:8px;margin:8px 0}.success{background:#e9f9ef;color:#087443}.error{background:#fff0ef;color:#b42318}.row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid #edf2f7}.row:last-child{border-bottom:0}.notice{padding:12px;background:#fff8e6;border:1px solid #f4d58d;border-radius:8px;margin:12px 0}.answer{margin-top:18px;padding:16px;background:#eaf9f7;border:1px solid #b7e7df;border-radius:10px}footer{text-align:center;padding:18px;color:#829ab1;font-size:11px}@media(max-width:720px){header{padding:15px 4%}nav{width:100%;overflow:auto;flex-wrap:nowrap}nav a{white-space:nowrap}main{margin-top:18px}.stats,.cols{grid-template-columns:1fr}.card{padding:17px}table{font-size:12px}}"""
BASE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{ title }} | Smart Health</title><style>""" + STYLE + """</style></head><body><header><a class="brand" href="/">✚ Smart Health</a><nav>{% for label,path in nav %}<a class="{{ 'active' if active==path else '' }}" href="{{ path }}">{{ label }}</a>{% endfor %}</nav></header><main>{% with msgs=get_flashed_messages(with_categories=true) %}{% for cat,msg in msgs %}<div class="flash {{cat}}">{{msg}}</div>{% endfor %}{% endwith %}{{ body|safe }}</main><footer>SMART HEALTH · HACKATHON PROTOTYPE · Demo only, not a medical device.</footer></body></html>"""
NAV = [("Dashboard","/"),("Patients","/patients"),("Appointments","/appointments"),("Inventory","/inventory"),("Assistant","/assistant")]

def page(title, active, body, **context):
    return render_template_string(BASE, title=title, active=active, nav=NAV, body=render_template_string(body, **context))

def next_id(items):
    return max((int(x.get("id", 0)) for x in items), default=0) + 1

def valid_text(value, maximum=100):
    value = (value or "").strip()
    return bool(value) and len(value) <= maximum and not any(ord(c) < 32 for c in value)

def parse_int(value, minimum=0, maximum=1_000_000):
    try:
        if not re.fullmatch(r"\d+", str(value or "").strip()): return None
        n = int(value)
        return n if minimum <= n <= maximum else None
    except (ValueError, TypeError):
        return None

@app.after_request
def security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response

@app.route("/")
def dashboard():
    low = [i for i in inventory if i["stock"] <= i["minimum"]]
    body = """<section class="hero"><p>HEALTHCARE OPERATIONS</p><h1>Care operations, at a glance.</h1><p class="muted">Manage demo patients, appointments and essential supplies in one place.</p><a class="btn" style="background:white;color:#102a43" href="/assistant">Ask Smart Health →</a></section><section class="stats"><article class="card stat">Total patients<strong>{{ patients|length }}</strong><a href="/patients">View directory →</a></article><article class="card stat">Appointments<strong>{{ appointments|length }}</strong><a href="/appointments">View schedule →</a></article><article class="card stat">Low-stock items<strong>{{ low|length }}</strong><a href="/inventory">Review inventory →</a></article></section><section class="cols"><article class="card"><h2>Low-stock alerts</h2>{% for i in low %}<div class="row"><span><b>{{i.name}}</b><small>{{i.category}}</small></span><span class="pill low">{{i.stock}} {{i.unit}} / min {{i.minimum}}</span></div>{% else %}<p>All supplies are above minimum.</p>{% endfor %}</article><article class="card"><h2>Upcoming appointments</h2>{% for a in appointments[:5] %}<div class="row"><span><b>{{a.patient}}</b><small>{{a.doctor}}</small></span><span>{{a.date}}<small>{{a.time}}</small></span></div>{% else %}<p>No appointments recorded.</p>{% endfor %}</article></section>"""
    return page("Dashboard","/",body,patients=patients,appointments=appointments,low=low)

@app.route("/patients", methods=["GET","POST"])
def patients_page():
    if request.method == "POST":
        name=request.form.get("name","").strip()
        age=parse_int(request.form.get("age"),0,120)
        gender=request.form.get("gender","").strip()
        phone=request.form.get("phone","").strip()
        condition=request.form.get("condition","").strip() or "Not specified"
        if not valid_text(name,100) or age is None or gender not in ("Female","Male","Other","Prefer not to say"):
            flash("Enter a valid name, age and gender.","error")
        elif phone and not re.fullmatch(r"[0-9+\-\s()]{7,20}",phone):
            flash("Enter a valid phone number.","error")
        elif not valid_text(condition,200):
            flash("Visit reason must be 1–200 characters.","error")
        else:
            patients.append({"id":next_id(patients),"name":name,"age":age,"gender":gender,"phone":phone,"condition":condition})
            flash("Patient added successfully.","success")
            return redirect(url_for("patients_page"))
    body="""<h1>Patients</h1><p class="muted">Demo records only. Do not enter real patient information.</p><section class="cols"><article class="card"><h2>Add a patient</h2><form method="post"><label>Full name</label><input name="name" maxlength="100" required><div class="cols"><div><label>Age</label><input name="age" type="number" min="0" max="120" required></div><div><label>Gender</label><select name="gender" required><option value="">Choose</option><option>Female</option><option>Male</option><option>Other</option><option>Prefer not to say</option></select></div></div><label>Phone (optional)</label><input name="phone" maxlength="20"><label>Visit reason</label><input name="condition" maxlength="200"><p><button>Add patient</button></p></form></article><article class="card"><h2>Patient directory ({{patients|length}})</h2>{% for p in patients %}<div class="row"><span><b>{{p.name}}</b><small>{{p.age}} years · {{p.gender}} · {{p.condition}}</small></span></div>{% else %}<p>No patients yet.</p>{% endfor %}</article></section>"""
    return page("Patients","/patients",body,patients=patients)

@app.route("/appointments", methods=["GET","POST"])
def appointments_page():
    if request.method=="POST":
        patient=request.form.get("patient","").strip()
        doctor=request.form.get("doctor","").strip()
        appt_date=request.form.get("date","").strip()
        appt_time=request.form.get("time","").strip()
        try: valid_date=date.fromisoformat(appt_date)>=date.today()
        except ValueError: valid_date=False
        if not any(p["name"]==patient for p in patients) or not valid_text(doctor,100) or not valid_date or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d",appt_time):
            flash("Choose a patient, valid doctor, current/future date and valid time.","error")
        else:
            appointments.append({"id":next_id(appointments),"patient":patient,"doctor":doctor,"date":appt_date,"time":appt_time})
            flash("Appointment saved.","success")
            return redirect(url_for("appointments_page"))
    body="""<h1>Appointments</h1><p class="muted">Schedule and review demo visits.</p><section class="cols"><article class="card"><h2>Schedule appointment</h2>{% if patients %}<form method="post"><label>Patient</label><select name="patient" required><option value="">Choose patient</option>{% for p in patients %}<option>{{p.name}}</option>{% endfor %}</select><label>Doctor / provider</label><input name="doctor" maxlength="100" required><div class="cols"><div><label>Date</label><input type="date" name="date" min="{{today}}" required></div><div><label>Time</label><input type="time" name="time" required></div></div><button>Save appointment</button></form>{% else %}<p>Add a patient before scheduling.</p><a class="btn" href="/patients">Add patient</a>{% endif %}</article><article class="card"><h2>Recorded visits</h2>{% for a in appointments %}<div class="row"><span><b>{{a.patient}}</b><small>{{a.doctor}}</small></span><span>{{a.date}}<small>{{a.time}}</small></span></div>{% else %}<p>No appointments recorded.</p>{% endfor %}</article></section>"""
    return page("Appointments","/appointments",body,patients=patients,appointments=sorted(appointments,key=lambda a:(a["date"],a["time"])),today=date.today().isoformat())

@app.route("/inventory", methods=["GET","POST"])
def inventory_page():
    if request.method=="POST":
        name=request.form.get("name","").strip(); category=request.form.get("category","").strip()
        stock=parse_int(request.form.get("stock")); minimum=parse_int(request.form.get("minimum")); unit=request.form.get("unit","units").strip()
        if not valid_text(name,100) or not valid_text(category,80): flash("Enter a valid item name and category.","error")
        elif stock is None or minimum is None: flash("Stock and minimum must be whole numbers from 0 to 1,000,000.","error")
        elif not valid_text(unit,30): flash("Unit must be 1–30 characters.","error")
        else:
            inventory.append({"id":next_id(inventory),"name":name,"category":category,"stock":stock,"minimum":minimum,"unit":unit})
            flash("Inventory item added.","success")
            return redirect(url_for("inventory_page"))
    low=[i for i in inventory if i["stock"]<=i["minimum"]]
    body="""<h1>Inventory</h1><p class="muted">Track essential supplies and low-stock alerts.</p>{% if low %}<div class="notice"><b>Attention:</b> {{low|length}} item(s) are at or below minimum stock.</div>{% endif %}<section class="cols"><article class="card"><h2>Add inventory item</h2><form method="post"><label>Item name</label><input name="name" maxlength="100" required><label>Category</label><input name="category" maxlength="80" required><div class="cols"><div><label>Current stock</label><input type="number" name="stock" min="0" max="1000000" required></div><div><label>Minimum stock</label><input type="number" name="minimum" min="0" max="1000000" required></div></div><label>Unit</label><input name="unit" maxlength="30" value="units" required><p><button>Add item</button></p></form></article><article class="card"><h2>All supplies ({{inventory|length}})</h2><div style="overflow:auto"><table><thead><tr><th>Item</th><th>Stock</th><th>Minimum</th><th>Status</th></tr></thead><tbody>{% for i in inventory %}<tr><td><b>{{i.name}}</b><small>{{i.category}}</small></td><td>{{i.stock}} {{i.unit}}</td><td>{{i.minimum}} {{i.unit}}</td><td>{% if i.stock<=i.minimum %}<span class="pill low">Low stock</span>{% else %}<span class="pill ok">In range</span>{% endif %}</td></tr>{% endfor %}</tbody></table></div></article></section>"""
    return page("Inventory","/inventory",body,inventory=inventory,low=low)

@app.route("/assistant", methods=["GET","POST"])
def assistant():
    answer=None; question=""
    if request.method=="POST":
        question=request.form.get("question","").strip()
        if not question or len(question)>1000: answer="Enter a question of 1–1000 characters."
        else:
            q=question.casefold()
            emergency=("emergency","chest pain","can't breathe","cannot breathe","difficulty breathing","unconscious","stroke","severe bleeding")
            supply=("stock","medicine","supply","supplies","inventory","shortage","low")
            if any(t in q for t in emergency):
                answer="This may be an emergency. Contact local emergency services immediately (112 in India) or go to the nearest emergency department. Do not rely on this demo for medical advice."
            elif any(t in q for t in supply):
                low=[i for i in inventory if int(i.get("stock",0))<=int(i.get("minimum",0))]
                summary=", ".join(f'{i["name"]} ({i["stock"]} {i["unit"]}; minimum {i["minimum"]})' for i in low)
                answer="Inventory summary: "+(summary or "No items are below their minimum stock level.")+" Confirm quantities with staff."
            elif any(t in q for t in ("appointment","doctor","schedule")):
                answer=f"There are {len(appointments)} demo appointments recorded. Confirm schedules with the clinic team."
            else:
                answer="This demo cannot diagnose or prescribe. For personal symptoms or treatment decisions, contact a qualified healthcare professional."
    body="""<section class="card" style="max-width:780px;margin:15px auto"><p style="color:#087f8c;font-size:11px;font-weight:bold;letter-spacing:2px">ASK SMART HEALTH</p><h1>Assistant chat</h1><p class="muted">Ask about supply levels, appointments or general health information.</p><p><span class="pill">Which supplies are low?</span> <span class="pill">I have chest pain</span></p><form method="post"><label>Your question</label><textarea name="question" maxlength="1000" rows="3" required placeholder="Ask about inventory, appointments, or general health information...">{{question}}</textarea><p><button>Get response →</button></p></form>{% if answer %}<div class="answer"><b>Response</b><p>{{answer}}</p></div>{% endif %}<p class="muted" style="font-size:12px;margin-top:18px">Safety notice: Not a medical device. Not for emergencies. In India, call 112 for emergencies.</p></section>"""
    return page("Assistant","/assistant",body,answer=answer,question=question)

@app.route("/health")
def health():
    return jsonify(status="ok",app="Smart Health",timestamp=datetime.now().astimezone().isoformat())

@app.errorhandler(404)
def not_found(_error):
    return page("Not found","",'<section class="card"><h1>Page not found</h1><p>The address may be incorrect.</p><a class="btn" href="/">Return to dashboard</a></section>'),404

@app.errorhandler(413)
def too_large(_error):
    return "Request too large.",413

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT","5000")),debug=False)
