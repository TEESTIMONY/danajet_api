from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class AuthEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_login_me_logout_flow(self):
        register_response = self.client.post(
            "/api/auth/register/",
            {
                "email": "reader@example.com",
                "password": "StrongPass123!",
                "first_name": "Dana",
                "last_name": "Jet",
            },
            format="json",
        )

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(register_response.data["user"]["email"], "reader@example.com")

        self.client.post("/api/auth/logout/")
        login_response = self.client.post(
            "/api/auth/login/",
            {"email": "reader@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        me_response = self.client.get("/api/auth/me/")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["user"]["email"], "reader@example.com")
        self.assertEqual(get_user_model().objects.count(), 1)
