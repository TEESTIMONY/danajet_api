from django.contrib import admin

from .models import CallToAction, MediaAsset, NavigationItem, PageSection, RequestFormOptionSet, SiteSetting, SocialLink


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "group", "is_public", "updated_at")
    list_filter = ("group", "is_public")
    search_fields = ("key", "label", "value")


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "area", "parent", "href", "is_visible", "display_order")
    list_filter = ("area", "is_visible")
    search_fields = ("label", "href")


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("page", "section_key", "title", "is_published", "display_order", "updated_at")
    list_filter = ("page", "is_published")
    search_fields = ("section_key", "title", "subtitle", "body")


@admin.register(CallToAction)
class CallToActionAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "button_label", "is_published", "display_order")
    list_filter = ("location", "is_published")
    search_fields = ("title", "copy", "button_label", "button_url")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "asset_type", "usage", "is_public", "updated_at")
    list_filter = ("asset_type", "is_public", "usage")
    search_fields = ("title", "alt_text", "usage", "external_url")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "url", "is_visible", "display_order")
    list_filter = ("is_visible",)
    search_fields = ("platform", "url")


@admin.register(RequestFormOptionSet)
class RequestFormOptionSetAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "is_active", "display_order", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("key", "label", "helper_text")
