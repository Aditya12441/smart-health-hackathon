import unittest
import app as smart_health


class SmartHealthTests(unittest.TestCase):
    def setUp(self):
        self.client = smart_health.app.test_client()
        self.original_patients = list(smart_health.patients)
        self.original_appointments = list(smart_health.appointments)
        self.original_inventory = list(smart_health.inventory)

    def tearDown(self):
        smart_health.patients[:] = self.original_patients
        smart_health.appointments[:] = self.original_appointments
        smart_health.inventory[:] = self.original_inventory

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Health", response.data)

    def test_health_endpoint_returns_json(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_security_headers_are_present(self):
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
        response = self.client.post("/patients", data={"name": "Test", "age": "999"})
        self.assertEqual(response.status_code, 200)
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

    def test_reject_negative_inventory(self):
        before = len(smart_health.inventory)
        self.client.post("/inventory", data={
            "name": "Test", "category": "PPE", "stock": "-1", "minimum": "5"
        })
        self.assertEqual(len(smart_health.inventory), before)

    def test_reject_unknown_appointment_patient(self):
        before = len(smart_health.appointments)
        self.client.post("/appointments", data={
            "patient": "Not Registered", "doctor": "Dr Test",
            "date": "2099-01-01", "time": "10:00"
        })
        self.assertEqual(len(smart_health.appointments), before)

    def test_assistant_flags_emergency(self):
        response = self.client.post("/assistant", data={"question": "I have chest pain"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"112 in India", response.data)

    def test_assistant_inventory_summary(self):
        response = self.client.post("/assistant", data={"question": "Which supplies are low?"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ORS Sachets", response.data)

    def test_unknown_route_is_404(self):
        self.assertEqual(self.client.get("/route-that-does-not-exist").status_code, 404)

    def test_all_main_pages_load(self):
        for path in ("/patients", "/appointments", "/inventory", "/assistant"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_dashboard_has_accessible_main_landmark(self):
        response = self.client.get("/")
        self.assertIn(b'id="main-content"', response.data)
        self.assertIn(b"Skip to main content", response.data)

    def test_reject_malformed_appointment_date(self):
        before = len(smart_health.appointments)
        self.client.post("/appointments", data={
            "patient": smart_health.patients[0]["name"], "doctor": "Dr Test",
            "date": "not-a-date", "time": "25:90"
        })
        self.assertEqual(len(smart_health.appointments), before)

    def test_reject_oversized_assistant_question(self):
        response = self.client.post("/assistant", data={"question": "x" * 1001})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"1-1000 characters", response.data)

    def test_inventory_low_stock_stats_are_consistent(self):
        response = self.client.get("/")
        expected = sum(item["stock"] < item["minimum"] for item in smart_health.inventory)
        self.assertEqual(smart_health.get_stats()["low_stock"], expected)

    def test_error_responses_do_not_leak_debug_details(self):
        response = self.client.get("/not-a-real-page")
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(b"Traceback", response.data)


if __name__ == "__main__":
    unittest.main()
