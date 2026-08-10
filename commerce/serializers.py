from decimal import Decimal

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from catalog.models import Course, Product
from catalog.serializers import CourseSerializer, ProductSerializer
from sitecontent.serializers import is_image_upload, media_public_url, optimize_image_upload

from .models import Cart, CartItem, Coupon, CourseEnrollment, Order, OrderItem, Payment, ShippingRate
from .emails import queue_order_emails


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    course_detail = CourseSerializer(source="course", read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ["cart", "created_at", "updated_at"]

    def validate(self, attrs):
        item_type = attrs.get("item_type", getattr(self.instance, "item_type", "product"))
        product = attrs.get("product", getattr(self.instance, "product", None))
        course = attrs.get("course", getattr(self.instance, "course", None))
        if item_type == "product" and not product:
            raise serializers.ValidationError("Product is required for product cart items.")
        if item_type == "course" and not course:
            raise serializers.ValidationError("Course is required for course cart items.")
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class AddCartItemSerializer(serializers.Serializer):
    item_type = serializers.ChoiceField(choices=["product", "course"], default="product")
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        if attrs["item_type"] == "product" and not attrs.get("product"):
            raise serializers.ValidationError("Product is required.")
        if attrs["item_type"] == "course" and not attrs.get("course"):
            raise serializers.ValidationError("Course is required.")
        return attrs


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


class ShippingRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRate
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = ["order", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["user", "order_number", "created_at", "updated_at", "receipt_uploaded_at"]

    def validate_receipt(self, value):
        if not value:
            return value
        if value.size > settings.MEDIA_UPLOAD_MAX_BYTES:
            raise serializers.ValidationError(f"Receipt must be {settings.MEDIA_UPLOAD_MAX_MB}MB or smaller.")

        if is_image_upload(value):
            optimized = optimize_image_upload(value)
            # optimize_image_upload only re-encodes files Pillow can actually decode as an
            # image; anything it could not decode (a mislabelled non-image, an SVG, a
            # polyglot file, ...) comes back unchanged, so require the .webp result here
            # instead of trusting the client-supplied content type.
            if not str(getattr(optimized, "name", "")).lower().endswith(".webp"):
                raise serializers.ValidationError("That file is not a valid image. Please upload a JPG, PNG, or PDF receipt.")
            return optimized

        value.seek(0)
        header = value.read(5)
        value.seek(0)
        if header != b"%PDF-":
            raise serializers.ValidationError("Receipts must be an image (JPG or PNG) or a PDF file.")
        return value

    def get_receipt_url(self, obj):
        if not obj.receipt:
            return ""
        public_url = media_public_url(obj.receipt.name)
        if public_url:
            return public_url
        request = self.context.get("request")
        url = obj.receipt.url
        return request.build_absolute_uri(url) if request else url


class CheckoutSerializer(serializers.Serializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), required=False, allow_null=True)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=80, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=120)
    last_name = serializers.CharField(max_length=120)
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    cart_session_key = serializers.CharField(required=False, allow_blank=True)
    shipping_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=Decimal("0.00"))
    tax_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=Decimal("0.00"))
    payment_method = serializers.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        required=False,
        default="international_request",
    )
    display_currency = serializers.CharField(max_length=10, required=False, default="USD")
    display_total = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, default=Decimal("0.00"))

    def validate_cart(self, value):
        request = self.context.get("request")
        if not value:
            return value
        if request and request.user.is_authenticated and value.user_id and value.user_id != request.user.id and not request.user.is_staff:
            raise serializers.ValidationError("You do not have access to this cart.")
        if not value.items.exists():
            raise serializers.ValidationError("Cart is empty.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        cart = attrs.get("cart")
        if cart and (not request or not request.user.is_authenticated):
            if not attrs.get("cart_session_key") or cart.session_key != attrs["cart_session_key"]:
                raise serializers.ValidationError("You do not have access to this cart.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        cart = validated_data.pop("cart", None)
        validated_data.pop("cart_session_key", None)
        coupon_code = validated_data.pop("coupon_code", "")
        billing_address = validated_data.pop("billing_address", None)
        coupon = Coupon.objects.filter(code__iexact=coupon_code, is_active=True).first() if coupon_code else None
        shipping_total = validated_data.pop("shipping_total", Decimal("0.00"))
        tax_total = validated_data.pop("tax_total", Decimal("0.00"))

        with transaction.atomic():
            subtotal = cart.subtotal if cart else Decimal("0.00")
            discount_total = Decimal("0.00")
            if coupon:
                if coupon.discount_type == "percent":
                    discount_total = subtotal * (coupon.amount / Decimal("100.00"))
                else:
                    discount_total = coupon.amount
                discount_total = min(discount_total, subtotal)

            total = subtotal - discount_total + shipping_total + tax_total
            order = Order.objects.create(
                user=request.user if request and request.user.is_authenticated else None,
                cart=cart,
                coupon=coupon,
                subtotal=subtotal,
                discount_total=discount_total,
                shipping_total=shipping_total,
                tax_total=tax_total,
                total=total,
                billing_address=billing_address or validated_data["shipping_address"],
                **validated_data,
            )
            if cart:
                for item in cart.items.select_related("product", "course"):
                    OrderItem.objects.create(
                        order=order,
                        item_type=item.item_type,
                        product=item.product,
                        course=item.course,
                        title=item.title,
                        sku=item.sku,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        metadata=item.metadata,
                    )
                cart.status = "ordered"
                cart.save(update_fields=["status", "updated_at"])
            if coupon:
                coupon.used_count += 1
                coupon.save(update_fields=["used_count", "updated_at"])
            Payment.objects.create(
                order=order,
                provider=order.payment_method,
                amount=order.total,
                currency=order.currency,
                status="pending",
                metadata={"display_currency": order.display_currency, "display_total": str(order.display_total)},
            )
            transaction.on_commit(lambda: queue_order_emails(order.pk))
        return order


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]
