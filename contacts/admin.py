from django.contrib import admin

from .models import ContactMessage, NewsletterSubscription, ProjectRequest, TransportWaitlist


@admin.register(ProjectRequest)
class ProjectRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "budget", "timeline", "status", "created_at")
    list_filter = ("status", "service", "preferred_contact_method", "budget", "timeline")
    search_fields = ("name", "email", "phone", "book_title", "message")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "reason", "subject", "status", "created_at")
    list_filter = ("status", "reason")
    search_fields = ("name", "email", "phone", "subject", "message")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "source", "is_active", "created_at")
    list_filter = ("is_active", "source")
    search_fields = ("name", "email", "source")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TransportWaitlist)
class TransportWaitlistAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "city", "status", "created_at")
    list_filter = ("status", "city")
    search_fields = ("email", "name", "phone", "city", "notes")
    readonly_fields = ("created_at", "updated_at")
