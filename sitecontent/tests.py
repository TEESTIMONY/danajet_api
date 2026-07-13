from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from .models import MediaAsset, NavigationItem, SiteSetting


TEST_MIDDLEWARE = [middleware for middleware in settings.MIDDLEWARE if "whitenoise" not in middleware]


@override_settings(MIDDLEWARE=TEST_MIDDLEWARE)
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

    @override_settings(MEDIA_IMAGE_MAX_WIDTH=900, MEDIA_IMAGE_MAX_HEIGHT=900, MEDIA_IMAGE_QUALITY=82)
    def test_staff_image_upload_is_optimized_to_webp(self):
        self.client.force_authenticate(self.staff)
        image_buffer = BytesIO()
        Image.new("RGB", (2400, 1400), "#ef5b4f").save(image_buffer, format="JPEG", quality=95)
        image_buffer.seek(0)

        response = self.client.post(
            "/api/media-assets/",
            {
                "title": "Large product image",
                "asset_type": "image",
                "usage": "Product gallery",
                "is_public": "true",
                "file": SimpleUploadedFile("large-product.jpg", image_buffer.read(), content_type="image/jpeg"),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        asset = MediaAsset.objects.get(pk=response.data["id"])
        self.assertTrue(asset.file.name.endswith(".webp"))
        asset.file.open("rb")
        optimized = Image.open(asset.file)
        self.assertEqual(optimized.format, "WEBP")
        self.assertLessEqual(max(optimized.size), 900)
