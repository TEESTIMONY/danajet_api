from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from .models import ContactMessage, NewsletterSubscription, ProjectRequest, TransportWaitlist
from .emails import queue_newsletter_welcome_email
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

    def create(self, request, *args, **kwargs):
        email = str(request.data.get("email", "")).strip().lower()
        if email:
            existing = NewsletterSubscription.objects.filter(email__iexact=email).first()
            if existing:
                existing.email = email
                existing.name = request.data.get("name", existing.name) or existing.name
                existing.source = request.data.get("source", existing.source) or existing.source
                existing.is_active = True
                existing.save(update_fields=["email", "name", "source", "is_active", "updated_at"])
                queue_newsletter_welcome_email(existing)
                serializer = self.get_serializer(existing)
                return Response(serializer.data, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        queue_newsletter_welcome_email(serializer.instance)


class TransportWaitlistViewSet(PublicCreateStaffManageViewSet):
    queryset = TransportWaitlist.objects.all()
    serializer_class = TransportWaitlistSerializer
    filterset_fields = ["status", "city"]
    search_fields = ["name", "email", "phone", "city", "notes"]
    ordering_fields = ["created_at", "updated_at", "status"]
