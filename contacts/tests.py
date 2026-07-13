from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
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

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="admin@danajet.com",
        NEWSLETTER_EMAIL_ASYNC=False,
    )
    def test_public_newsletter_subscription_sends_welcome_email(self):
        response = self.client.post(
            "/api/newsletter-subscriptions/",
            {"email": "reader@example.com", "source": "Footer newsletter"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, "admin@danajet.com")
        self.assertEqual(mail.outbox[0].to, ["reader@example.com"])
        self.assertIn("Welcome to the Danajet Network", mail.outbox[0].subject)
        self.assertIn("book resources", mail.outbox[0].body)
