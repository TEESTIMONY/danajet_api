from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Product


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )

    def test_public_can_read_published_products(self):
        Product.objects.create(title="Published Book", slug="published-book", is_published=True)
        Product.objects.create(title="Draft Book", slug="draft-book", is_published=False)

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        titles = [item["title"] for item in payload["results"]]
        self.assertIn("Published Book", titles)
        self.assertNotIn("Draft Book", titles)

    def test_staff_can_create_product(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            "/api/products/",
            {"title": "Admin Book", "summary": "Created through API", "price": "12.99"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Product.objects.filter(title="Admin Book").exists())
