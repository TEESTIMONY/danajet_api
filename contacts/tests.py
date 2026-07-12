from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class ContactApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )

    def test_public_can_create_project_request(self):
        response = self.client.post(
            "/api/project-requests/",
            {
                "name": "Jane Author",
                "email": "jane@example.com",
                "service": "Book formatting",
                "message": "I need help preparing my book.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "New")

    def test_public_cannot_list_project_requests(self):
        response = self.client.get("/api/project-requests/")

        self.assertEqual(response.status_code, 403)

    def test_staff_can_list_project_requests(self):
        self.client.force_authenticate(self.staff)

        response = self.client.get("/api/project-requests/")

        self.assertEqual(response.status_code, 200)
