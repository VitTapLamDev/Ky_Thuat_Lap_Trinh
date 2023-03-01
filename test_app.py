import unittest
import jwt
from fastapi.testclient import TestClient
from app import app


_JWT_SECRET = "ad2t4h13adsfg9aw"

client = TestClient(app)

class TestAPI(unittest.TestCase):

    def test_get_data(self):
        response = client.get('/api/v1/posts/all-user')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_post_data(self):
        data = {"post_title": "Bai Test Post", "post_description": "Test linh tinh", "image": "test"}
        response = client.post('/api/v1/posts', json=data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()["message"], "Data added successfully")

    def test_put_data(self):
        post_id = '1'
        data = {"post_title": "Bai Test Post", "post_description": "Test linh tinh", "image": "test"}
        response = client.put(f'/api/v1/posts/{post_id}/', json=data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()["message"], "Data updated successfully")

    def test_delete_data(self):
        post_id = '10'
        response = client.delete(f"/apt/v1/post-delete/{post_id}")
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()["message"], "Data deleted successfully")

if __name__ == "__main__":
    unittest.main(verbosity=2)
