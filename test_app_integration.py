import os
import unittest
from app import app
from database.db import get_user_by_email, get_user_assessments

class TestTravelReadyApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_1_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Travel Smart', response.data)
        self.assertIn(b'Passport Validity Verification', response.data)
        print("Test 1 Passed: Home page loads with all feature sections.")

    def test_2_registration_and_login(self):
        # Register a test user
        reg_response = self.client.post('/register', data={
            'full_name': 'Maha Lakshmi',
            'email': 'maha.test@example.com',
            'phone': '9876543210',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        user = get_user_by_email('maha.test@example.com')
        self.assertIsNotNone(user)
        print(f"Test 2 Passed: User registered successfully (User ID: {user['user_id']}).")

    def test_3_assessment_submission_and_prediction(self):
        # Log in first
        self.client.post('/login', data={
            'email': 'maha.test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        # Submit ready travel assessment
        resp_ready = self.client.post('/assessment', data={
            'destination_country': 'United Kingdom',
            'travel_purpose': 'Tourism',
            'travel_date': '2026-12-01',
            'return_date': '2026-12-15',
            'passport_status': 'Valid',
            'passport_expiry_date': '2027-12-01',
            'visa_status': 'Approved',
            'return_ticket': 'Yes',
            'hotel_booking': 'Yes',
            'travel_insurance': 'Yes',
            'vaccination_status': 'Yes'
        }, follow_redirects=True)
        self.assertEqual(resp_ready.status_code, 200)
        self.assertIn(b'Ready to Travel', resp_ready.data)
        print("Test 3 Passed: 'Ready to Travel' predicted & displayed correctly.")

        # Submit not ready travel assessment
        resp_not_ready = self.client.post('/assessment', data={
            'destination_country': 'Japan',
            'travel_purpose': 'Business',
            'travel_date': '2026-12-01',
            'return_date': '2026-12-15',
            'passport_status': 'Invalid',
            'passport_expiry_date': '2026-12-05',
            'visa_status': 'None',
            'return_ticket': 'No',
            'hotel_booking': 'No',
            'travel_insurance': 'No',
            'vaccination_status': 'No'
        }, follow_redirects=True)
        self.assertEqual(resp_not_ready.status_code, 200)
        self.assertIn(b'Not Ready to Travel', resp_not_ready.data)
        print("Test 4 Passed: 'Not Ready to Travel' predicted & displayed correctly.")

    def test_4_pdf_download_and_report_view(self):
        # Log in
        self.client.post('/login', data={
            'email': 'maha.test@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        user = get_user_by_email('maha.test@example.com')
        assessments = get_user_assessments(user['user_id'])
        self.assertGreater(len(assessments), 0)
        a_id = assessments[0]['assessment_id']

        # View interactive report
        rep_resp = self.client.get(f'/report/{a_id}')
        self.assertEqual(rep_resp.status_code, 200)
        self.assertIn(b'BRIEFIQ', rep_resp.data)

        # Download PDF
        pdf_resp = self.client.get(f'/download-report/{a_id}')
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp.mimetype, 'application/pdf')
        print(f"Test 5 Passed: PDF Report downloaded successfully ({len(pdf_resp.data)} bytes).")

if __name__ == '__main__':
    unittest.main()

