from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import NavigationItem, SiteSetting


class SiteContentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )

    def test_public_can_read_visible_navigation(self):
        NavigationItem.objects.create(label="Home", href="/", area="header", is_visible=True)
        NavigationItem.objects.create(label="Hidden", href="/hidden", area="header", is_visible=False)

        response = self.client.get("/api/navigation/")

        self.assertEqual(response.status_code, 200)
        labels = [item["label"] for item in response.json()["results"]]
        self.assertIn("Home", labels)
        self.assertNotIn("Hidden", labels)

    def test_staff_can_create_site_setting(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            "/api/site-settings/",
            {"key": "seo-title", "label": "SEO Title", "value": "Danajet"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(SiteSetting.objects.filter(key="seo-title").exists())
