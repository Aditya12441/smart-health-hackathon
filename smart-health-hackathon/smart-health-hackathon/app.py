from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'replace-this-before-production'

# Demo-only in-memory data. Do not use real patient information.
patients = [
    {'id': 1, 'name': 'Aarav Sharma', 'age': 28, 'condition': 'Routine check-up'},
    {'id': 2, 'name': 'Meera Patel', 'age': 42, 'condition': 'Follow-up'},
]
appointments = [
    {'id': 1, 'patient': 'Aarav Sharma', 'doctor': 'Dr. Rao', 'date': '2026-10-18', 'time': '10:30', 'status': 'Scheduled'},
    {'id': 2, 'patient': 'Meera Patel', 'doctor': 'Dr. Khan', 'date': '2026-10-18', 'time': '12:00', 'status': 'Waiting'},
]
inventory = [
    {'id': 1, 'name': 'Paracetamol 500 mg', 'category': 'Pain relief', 'stock': 120, 'minimum': 40, 'unit': 'tablets'},
    {'id': 2, 'name': 'ORS Sachets', 'category': 'Rehydration', 'stock': 18, 'minimum': 30, 'unit': 'sachets'},
    {'id': 3, 'name': 'Disposable Gloves', 'category': 'PPE', 'stock': 75, 'minimum': 25, 'unit': 'pairs'},
    {'id': 4, 'name': 'Surgical Masks', 'category': 'PPE', 'stock': 12, 'minimum': 50, 'unit': 'pieces'},
]


def get_stats():
    return {
        'patients': len(patients),
        'appointments': len(appointments),
        'inventory_items': len(inventory),
        'low_stock': sum(1 for item in inventory if item['stock'] < item['minimum']),
    }


@app.route('/')
def dashboard():
    low_stock_items = [item for item in inventory if item['stock'] < item['minimum']]
    return render_template('index.html', stats=get_stats(), patients=patients,
                           appointments=appointments, inventory=inventory,
                           low_stock_items=low_stock_items, active='dashboard')


@app.route('/patients', methods=['GET', 'POST'])
def patient_page():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        condition = request.form.get('condition', 'Routine check-up').strip()
        if not name or not age.isdigit() or not 0 < int(age) < 121:
            flash('Enter a name and a valid age between 1 and 120.', 'error')
        else:
            patients.append({'id': max([p['id'] for p in patients], default=0) + 1,
                             'name': name, 'age': int(age), 'condition': condition or 'Not specified'})
            flash('Demo patient added successfully.', 'success')
            return redirect(url_for('patient_page'))
    return render_template('patients.html', patients=patients, active='patients')


@app.route('/appointments', methods=['GET', 'POST'])
def appointment_page():
    if request.method == 'POST':
        patient = request.form.get('patient', '').strip()
        doctor = request.form.get('doctor', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()
        if not all([patient, doctor, date, time]):
            flash('Complete every appointment field.', 'error')
        else:
            appointments.append({'id': max([a['id'] for a in appointments], default=0) + 1,
                                 'patient': patient, 'doctor': doctor, 'date': date,
                                 'time': time, 'status': 'Scheduled'})
            flash('Demo appointment added.', 'success')
            return redirect(url_for('appointment_page'))
    return render_template('appointments.html', appointments=appointments, patients=patients, active='appointments')


@app.route('/inventory', methods=['GET', 'POST'])
def inventory_page():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        stock = request.form.get('stock', '').strip()
        minimum = request.form.get('minimum', '').strip()
        unit = request.form.get('unit', 'units').strip() or 'units'
        if not name or not category or not stock.isdigit() or not minimum.isdigit():
            flash('Enter a name, category, and valid stock numbers.', 'error')
        else:
            inventory.append({'id': max([i['id'] for i in inventory], default=0) + 1,
                              'name': name, 'category': category, 'stock': int(stock),
                              'minimum': int(minimum), 'unit': unit})
            flash('Inventory item added.', 'success')
            return redirect(url_for('inventory_page'))
    return render_template('inventory.html', inventory=inventory, active='inventory')


@app.route('/assistant', methods=['GET', 'POST'])
def assistant():
    answer = None
    question = ''
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        q = question.lower()
        if any(word in q for word in ['emergency', 'chest pain', "can't breathe", 'cannot breathe', 'unconscious', 'stroke', 'severe bleeding']):
            answer = 'This may be an emergency. Contact your local emergency service immediately (112 in India) or go to the nearest emergency department. Do not rely on this demo assistant.'
        elif any(word in q for word in ['stock', 'medicine', 'supply', 'inventory', 'shortage']):
            low = [item for item in inventory if item['stock'] < item['minimum']]
            answer = 'Inventory summary: ' + (', '.join(f"{i['name']} ({i['stock']} {i['unit']}; minimum {i['minimum']})" for i in low) if low else 'No items are currently below their minimum stock level.') + ' Confirm quantities and expiry dates with authorized staff before ordering.'
        elif any(word in q for word in ['appointment', 'doctor', 'schedule']):
            answer = f'There are {len(appointments)} demo appointments recorded. Please confirm schedules directly with the clinic team.'
        else:
            answer = 'I can provide general health information, but I cannot diagnose, prescribe, or replace a licensed clinician. For personal symptoms or treatment decisions, contact a qualified healthcare professional. For urgent or severe symptoms, seek emergency care.'
    return render_template('assistant.html', answer=answer, question=question, active='assistant')


@app.route('/health')
def health():
    return {'status': 'ok', 'app': 'Smart Health', 'timestamp': datetime.utcnow().isoformat() + 'Z'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
