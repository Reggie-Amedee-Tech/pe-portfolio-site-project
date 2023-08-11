# tests.py

import unittest
import os
os.environ['TESTING'] = 'true'

from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response =  self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>MLH Fellow</title>" in html
        #TODO add more tests relating to the home page

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")
        json = response.get_json()
        assert response.content_type == 'application/json'
        assert response.status_code == 200
        assert response.is_json

        # Testing post request
        response = self.client.post("/api/timeline_post", data={"name":"John Doe", "email":"john@example.com", "content":"Hello world, I'm John!"})
        assert response.status_code == 200
        
        # Checking for new post in timeline
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json

    def test_malformed_timeline_post(self):
        response = self.client.post("/api/timeline_post", data={"email":"john@example.com", "content":"Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html
        
        response = self.client.post("/api/timeline_post", data={"name":"John Doe", "email": "john@example.com", "content":""})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html

        response = self.client.post("/api/timeline_post", data={"name":"John Doe", "email":"not-an-email", "content":"Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html
