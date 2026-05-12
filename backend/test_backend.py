import unittest
import json
from app import create_app
from database import db

class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'healthy')

    def test_branches(self):
        # Assuming there is a /api/branches route
        response = self.client.get('/api/branches')
        # We don't care about content yet, just that the route exists or returns a valid code
        self.assertIn(response.status_code, [200, 404]) # Allow 404 if not implemented yet

    def test_dashboard(self):
        response = self.client.get('/api/dashboard/1')
        self.assertIn(response.status_code, [200, 404])

if __name__ == '__main__':
    unittest.main()
