from rest_framework import permissions, viewsets

from .models import CallToAction, MediaAsset, NavigationItem, PageSection, RequestFormOptionSet, SiteSetting, SocialLink
from .serializers import (
    CallToActionSerializer,
    MediaAssetSerializer,
    NavigationItemSerializer,
    PageSectionSerializer,
    RequestFormOptionSetSerializer,
    SiteSettingSerializer,
    SocialLinkSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class PublicContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]


class NavigationItemViewSet(PublicContentViewSet):
    queryset = NavigationItem.objects.select_related("parent").prefetch_related("children")
    serializer_class = NavigationItemSerializer
    filterset_fields = ["area", "is_visible", "parent"]
    search_fields = ["label", "href"]
    ordering_fields = ["area", "display_order", "label", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_visible=True)
        return queryset


class PageSectionViewSet(PublicContentViewSet):
    queryset = PageSection.objects.select_related("media")
    serializer_class = PageSectionSerializer
    filterset_fields = ["page", "section_key", "is_published"]
    search_fields = ["page", "section_key", "eyebrow", "title", "subtitle", "body"]
    ordering_fields = ["page", "display_order", "created_at", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_published=True)
        return queryset


class CallToActionViewSet(PublicContentViewSet):
    lookup_field = "slug"
    queryset = CallToAction.objects.all()
    serializer_class = CallToActionSerializer
    filterset_fields = ["location", "is_published"]
    search_fields = ["title", "copy", "button_label", "location"]
    ordering_fields = ["display_order", "title", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_published=True)
        return queryset


class MediaAssetViewSet(PublicContentViewSet):
    lookup_field = "slug"
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    filterset_fields = ["asset_type", "usage", "is_public"]
    search_fields = ["title", "alt_text", "usage", "external_url"]
    ordering_fields = ["asset_type", "title", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_public=True)
        return queryset


class SiteSettingViewSet(PublicContentViewSet):
    lookup_field = "key"
    queryset = SiteSetting.objects.all()
    serializer_class = SiteSettingSerializer
    filterset_fields = ["group", "is_public"]
    search_fields = ["key", "label", "value", "group"]
    ordering_fields = ["group", "key", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_public=True)
        return queryset


class SocialLinkViewSet(PublicContentViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    filterset_fields = ["platform", "is_visible"]
    search_fields = ["platform", "url"]
    ordering_fields = ["display_order", "platform", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_visible=True)
        return queryset


class RequestFormOptionSetViewSet(PublicContentViewSet):
    lookup_field = "key"
    queryset = RequestFormOptionSet.objects.all()
    serializer_class = RequestFormOptionSetSerializer
    filterset_fields = ["is_active"]
    search_fields = ["key", "label", "helper_text"]
    ordering_fields = ["display_order", "label", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset
