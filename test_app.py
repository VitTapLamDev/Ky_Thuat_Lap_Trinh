import unittest
from fastapi.testclient import TestClient
from app import app
import requests, json
import urllib.parse
client = TestClient(app)

class TestAPI(unittest.TestCase):

    def test_get_data(self):
        response = client.get('/api/v1/posts/all-user')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        if response.status_code==200:
            print('Connected Successful!!')

    def test_login(self):
        url = 'http://127.0.0.1:8000/api/v1/login'
        username = 'string@gmail.com'
        password = 'string'
        payload = {
            'username': username, 'password': password
        }
        data_encoded = urllib.parse.urlencode(payload)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, data=data_encoded, headers=headers)
        self.assertEqual(response.status_code, 200)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            token = response_json["access_token"]
            with open("token.txt", "w") as f:
                f.write(token)

    def test_create_user(self):
        user_data = {"email":"viet@gmail.com",
                     "name":"NguyenDucViet",
                     "phone_number":"0865946287",
                     "address":"LaoCai",
                     "password":"Vietlcvn"
        }
        response = client.post(f"/api/v1/users", json=user_data)
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        url = "http://127.0.0.1:8000/api/v1/posts"
        with open("token.txt", "r") as f:
            token = f.read().strip()
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }
        payload = {"post_title": "string",
                "post_description": "string",
                "image": "string"
        }
        print(token)
        response = client.post(url, json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_put_post(self):
        post_id = '2'
        data = {"post_title": "Bai Test Post", "post_description": "Test linh tinh", "image": "test"}
        response = client.put(f'/api/v1/update-posts/{post_id}/', json=data)
        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        post_id = '3'
        response = client.delete(f"/apt/v1/post-delete/{post_id}")
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main(verbosity=2)
