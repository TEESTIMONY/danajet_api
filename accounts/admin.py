from django.contrib import admin

from .models import CustomerAddress, CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "company", "marketing_opt_in", "created_at")
    search_fields = ("user__email", "user__username", "phone", "company")
    list_filter = ("marketing_opt_in", "created_at")


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address_type", "city", "country", "is_default", "created_at")
    search_fields = ("user__email", "first_name", "last_name", "city", "country")
    list_filter = ("address_type", "is_default", "country")
