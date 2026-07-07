from django.contrib import admin

from .models import Course, PortfolioProject, Product, Review, Service


@admin.register(Product, Course, PortfolioProject, Service, Review)
class PublishableAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "display_order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "summary", "slug")
    prepopulated_fields = {"slug": ("title",)}
