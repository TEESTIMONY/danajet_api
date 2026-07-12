from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import Course, Product


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Cart(TimestampedModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("ordered", "Ordered"),
        ("abandoned", "Abandoned"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="carts")
    session_key = models.CharField(max_length=120, blank=True, db_index=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="active")
    currency = models.CharField(max_length=10, default="USD")

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        owner = self.user.email if self.user_id and self.user.email else self.session_key or "guest"
        return f"Cart {self.pk} - {owner}"

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class CartItem(TimestampedModel):
    ITEM_TYPES = [
        ("product", "Product"),
        ("course", "Course"),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=40, choices=ITEM_TYPES, default="product")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="cart_items")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True, related_name="cart_items")
    title = models.CharField(max_length=180)
    sku = models.CharField(max_length=80, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.quantity}x {self.title}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Coupon(TimestampedModel):
    DISCOUNT_TYPES = [
        ("percent", "Percent"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(max_length=60, unique=True)
    discount_type = models.CharField(max_length=40, choices=DISCOUNT_TYPES, default="percent")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    used_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class ShippingRate(TimestampedModel):
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="USD")
    estimated_days = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["amount", "name"]

    def __str__(self):
        return self.name


class Order(TimestampedModel):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders")
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders")
    order_number = models.CharField(max_length=40, unique=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=80, blank=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    shipping_address = models.JSONField(default=dict, blank=True)
    billing_address = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    currency = models.CharField(max_length=10, default="USD")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders")
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=40, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_id = (Order.objects.order_by("-id").values_list("id", flat=True).first() or 0) + 1
            self.order_number = f"DJ-{last_id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=40, default="product")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="order_items")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True, related_name="order_items")
    title = models.CharField(max_length=180)
    sku = models.CharField(max_length=80, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.title}"


class Payment(TimestampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("requires_action", "Requires Action"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=80, default="manual")
    provider_reference = models.CharField(max_length=180, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="pending")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider} - {self.order.order_number}"


class CourseEnrollment(TimestampedModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, related_name="course_enrollments")
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default="active")
    progress = models.PositiveSmallIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "course"]

    def __str__(self):
        return f"{self.user} - {self.course}"
