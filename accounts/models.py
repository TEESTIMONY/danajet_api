from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField(max_length=80, blank=True)
    company = models.CharField(max_length=140, blank=True)
    marketing_opt_in = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__email"]

    def __str__(self):
        return self.user.get_full_name() or self.user.email or self.user.username


class CustomerAddress(models.Model):
    ADDRESS_TYPES = [
        ("shipping", "Shipping"),
        ("billing", "Billing"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=40, choices=ADDRESS_TYPES, default="shipping")
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=80, blank=True)
    line1 = models.CharField(max_length=220)
    line2 = models.CharField(max_length=220, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=120)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}"
