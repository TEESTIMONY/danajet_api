from django.contrib import admin

from .models import BlogPost, Brand, Category, Course, PortfolioProject, Product, Review, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "is_visible", "display_order", "updated_at")
    list_filter = ("category_type", "is_visible")
    search_fields = ("name", "description", "slug")
    prepopulated_fields = {"slug": ("name",)}


class PublishableAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "display_order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "summary", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Product)
class ProductAdmin(PublishableAdmin):
    list_display = ("title", "category", "price", "featured", "is_published", "display_order")
    list_filter = ("is_published", "featured", "is_digital", "category")
    search_fields = ("title", "subtitle", "summary", "author", "sku")


@admin.register(Course)
class CourseAdmin(PublishableAdmin):
    list_display = ("title", "category", "status", "level", "featured", "is_published")
    list_filter = ("is_published", "featured", "status", "level", "category")


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(PublishableAdmin):
    list_display = ("title", "category", "client", "service_type", "featured", "is_published")
    list_filter = ("is_published", "featured", "category", "service_type", "year")


@admin.register(Service)
class ServiceAdmin(PublishableAdmin):
    list_display = ("title", "availability", "starting_price", "is_published", "display_order")
    list_filter = ("is_published", "availability")


@admin.register(Review)
class ReviewAdmin(PublishableAdmin):
    list_display = ("reviewer_name", "rating", "service", "source", "featured", "is_published")
    list_filter = ("is_published", "featured", "rating", "service", "source")
    search_fields = ("title", "quote", "reviewer_name", "project")


@admin.register(Brand)
class BrandAdmin(PublishableAdmin):
    list_display = ("name", "code", "status", "href", "is_published", "display_order")
    list_filter = ("is_published", "status")
    search_fields = ("title", "name", "summary", "code")


@admin.register(BlogPost)
class BlogPostAdmin(PublishableAdmin):
    list_display = ("title", "author", "published_at", "is_published", "display_order")
    list_filter = ("is_published", "author")
