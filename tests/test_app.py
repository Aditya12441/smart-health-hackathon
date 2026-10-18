import unittest
from datetime import date, timedelta
import app as smart_health

class SmartHealthTests(unittest.TestCase):
    def setUp(self):
        self.client = smart_health.app.test_client()
        self.patients = list(smart_health.patients)
        self.appointments = list(smart_health.appointments)
        self.inventory = list(smart_health.inventory)

    def tearDown(self):
        smart_health.patients[:] = self.patients
        smart_health.appointments[:] = self.appointments
        smart_health.inventory[:] = self.inventory

    def test_dashboard_loads(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_security_headers(self):
        response = self.client.get("/")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")

    def test_add_patient(self):
        response = self.client.post("/patients", data={
            "name": "Test Patient", "age": "31", "condition": "Check-up"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(p["name"] == "Test Patient" for p in smart_health.patients))

    def test_reject_invalid_patient_age(self):
        before = len(smart_health.patients)
        self.client.post("/patients", data={"name": "Test", "age": "999"})
        self.assertEqual(len(smart_health.patients), before)

    def test_reject_empty_patient_name(self):
        before = len(smart_health.patients)
        self.client.post("/patients", data={"name": " ", "age": "30"})
        self.assertEqual(len(smart_health.patients), before)

    def test_add_inventory_item(self):
        response = self.client.post("/inventory", data={
            "name": "Test gloves", "category": "PPE", "stock": "2",
            "minimum": "5", "unit": "boxes"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(i["name"] == "Test gloves" for i in smart_health.inventory))

    def test_reject_negative_stock(self):
        before = len(smart_health.inventory)
        self.client.post("/inventory", data={
            "name": "Test", "category": "PPE", "stock": "-1", "minimum": "5"
        })
        self.assertEqual(len(smart_health.inventory), before)

    def test_reject_unknown_appointment_patient(self):
        before = len(smart_health.appointments)
        self.client.post("/appointments", data={
            "patient": "Unknown", "doctor": "Dr Test",
            "date": (date.today() + timedelta(days=2)).isoformat(), "time": "10:00"
        })
        self.assertEqual(len(smart_health.appointments), before)

    def test_reject_past_appointment(self):
        before = len(smart_health.appointments)
        self.client.post("/appointments", data={
            "patient": smart_health.patients[0]["name"], "doctor": "Dr Test",
            "date": (date.today() - timedelta(days=1)).isoformat(), "time": "10:00"
        })
        self.assertEqual(len(smart_health.appointments), before)

    def test_assistant_emergency_response(self):
        response = self.client.post("/assistant", data={"question": "I have chest pain"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"112 in India", response.data)

    def test_assistant_inventory_response(self):
        response = self.client.post("/assistant", data={"question": "Which supplies are low?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ORS Sachets", response.data)

    def test_unknown_route(self):
        self.assertEqual(self.client.get("/does-not-exist").status_code, 404)

if __name__ == "__main__":
    unittest.main()
