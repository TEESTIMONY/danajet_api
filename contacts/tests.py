from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest.mock import patch
import json

from .models import NewsletterSubscription


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
        RESEND_API_KEY="",
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

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="admin@danajet.com",
        NEWSLETTER_EMAIL_ASYNC=False,
        RESEND_API_KEY="",
    )
    def test_existing_newsletter_email_can_subscribe_again(self):
        NewsletterSubscription.objects.create(
            email="reader@example.com",
            source="Old popup",
            is_active=False,
        )

        response = self.client.post(
            "/api/newsletter-subscriptions/",
            {"email": "READER@example.com", "source": "Footer newsletter"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(NewsletterSubscription.objects.count(), 1)
        subscription = NewsletterSubscription.objects.get()
        self.assertEqual(subscription.email, "reader@example.com")
        self.assertEqual(subscription.source, "Footer newsletter")
        self.assertTrue(subscription.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["reader@example.com"])

    @override_settings(
        NEWSLETTER_EMAIL_ASYNC=False,
        RESEND_API_KEY="test-resend-key",
        RESEND_FROM_EMAIL="Danajet <onboarding@resend.dev>",
        RESEND_API_URL="https://api.resend.com/emails",
        EMAIL_TIMEOUT=10,
    )
    @patch("contacts.emails.urlrequest.urlopen")
    def test_public_newsletter_subscription_sends_with_resend_api(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = b'{"id":"email_123"}'

        response = self.client.post(
            "/api/newsletter-subscriptions/",
            {"email": "reader@example.com", "source": "Popup newsletter"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        mock_urlopen.assert_called_once()
        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["from"], "Danajet <onboarding@resend.dev>")
        self.assertEqual(payload["to"], ["reader@example.com"])
        self.assertIn("Welcome to the Danajet Network", payload["subject"])
        self.assertEqual(request.headers["Authorization"], "Bearer test-resend-key")
