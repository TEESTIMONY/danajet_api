from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from catalog.models import Product
from .models import Cart, Coupon, Order


class CommerceEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="buyer@example.com",
            email="buyer@example.com",
            password="StrongPass123!",
        )
        self.product = Product.objects.create(
            title="Book Idea Blueprint",
            slug="book-idea-blueprint",
            price=Decimal("7.00"),
            is_published=True,
        )

    def test_cart_add_item_and_checkout(self):
        self.client.force_authenticate(self.user)
        cart_response = self.client.post("/api/carts/", {"currency": "USD"}, format="json")
        self.assertEqual(cart_response.status_code, 201)

        item_response = self.client.post(
            f"/api/carts/{cart_response.data['id']}/items/",
            {"item_type": "product", "product": self.product.id, "quantity": 3},
            format="json",
        )
        self.assertEqual(item_response.status_code, 201)
        self.assertEqual(item_response.data["quantity"], 3)

        checkout_response = self.client.post(
            "/api/checkout/",
            {
                "cart": cart_response.data["id"],
                "email": "buyer@example.com",
                "first_name": "Test",
                "last_name": "Buyer",
                "shipping_address": {
                    "line1": "1 Danajet Way",
                    "city": "Lagos",
                    "country": "Nigeria",
                },
                "shipping_total": "5.99",
            },
            format="json",
        )

        self.assertEqual(checkout_response.status_code, 201)
        self.assertEqual(checkout_response.data["items"][0]["quantity"], 3)
        self.assertEqual(checkout_response.data["subtotal"], "21.00")
        self.assertEqual(checkout_response.data["total"], "26.99")
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Cart.objects.get(pk=cart_response.data["id"]).status, "ordered")

    def test_coupon_validate_endpoint(self):
        Coupon.objects.create(code="BOOK10", discount_type="percent", amount=Decimal("10.00"))
        response = self.client.post("/api/coupons/validate/", {"code": "BOOK10"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["valid"])
