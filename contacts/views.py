from rest_framework import mixins, permissions, viewsets

from .models import ContactMessage, NewsletterSubscription, ProjectRequest, TransportWaitlist
from .serializers import (
    ContactMessageSerializer,
    NewsletterSubscriptionSerializer,
    ProjectRequestSerializer,
    TransportWaitlistSerializer,
)


class PublicCreateStaffManageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_staff:
            serializer.save()
            return
        safe_defaults = {}
        if "status" in serializer.fields:
            safe_defaults["status"] = "New"
        if "internal_notes" in serializer.fields:
            safe_defaults["internal_notes"] = ""
        if "is_active" in serializer.fields:
            safe_defaults["is_active"] = True
        serializer.save(**safe_defaults)


class ProjectRequestViewSet(PublicCreateStaffManageViewSet):
    queryset = ProjectRequest.objects.all()
    serializer_class = ProjectRequestSerializer
    filterset_fields = ["status", "service", "preferred_contact_method"]
    search_fields = ["name", "email", "phone", "service", "book_title", "message"]
    ordering_fields = ["created_at", "updated_at", "status"]


class ContactMessageViewSet(PublicCreateStaffManageViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    filterset_fields = ["status", "reason"]
    search_fields = ["name", "email", "phone", "subject", "reason", "message"]
    ordering_fields = ["created_at", "updated_at", "status"]


class NewsletterSubscriptionViewSet(PublicCreateStaffManageViewSet):
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    filterset_fields = ["source", "is_active"]
    search_fields = ["name", "email", "source"]
    ordering_fields = ["created_at", "updated_at"]


class TransportWaitlistViewSet(PublicCreateStaffManageViewSet):
    queryset = TransportWaitlist.objects.all()
    serializer_class = TransportWaitlistSerializer
    filterset_fields = ["status", "city"]
    search_fields = ["name", "email", "phone", "city", "notes"]
    ordering_fields = ["created_at", "updated_at", "status"]
