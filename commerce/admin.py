from django.contrib import admin

from .models import Cart, CartItem, Coupon, CourseEnrollment, Order, OrderItem, Payment, ShippingRate


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "status", "currency", "updated_at")
    list_filter = ("status", "currency")
    search_fields = ("user__email", "session_key")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "email", "status", "payment_status", "total", "created_at")
    list_filter = ("status", "payment_status", "currency", "created_at")
    search_fields = ("order_number", "email", "first_name", "last_name")
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "amount", "is_active", "used_count")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "region", "amount", "currency", "is_active")
    list_filter = ("is_active", "country", "currency")
    search_fields = ("name", "country", "region")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "amount", "currency", "status", "created_at")
    list_filter = ("provider", "status", "currency")
    search_fields = ("order__order_number", "provider_reference")


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "progress", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "course__title")
