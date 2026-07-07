from rest_framework import mixins, viewsets

from .models import ContactMessage, ProjectRequest
from .serializers import ContactMessageSerializer, ProjectRequestSerializer


class CreateListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    pass


class ProjectRequestViewSet(CreateListViewSet):
    queryset = ProjectRequest.objects.all()
    serializer_class = ProjectRequestSerializer
    search_fields = ["name", "email", "service", "message"]
    ordering_fields = ["created_at", "status"]


class ContactMessageViewSet(CreateListViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    search_fields = ["name", "email", "subject", "message"]
    ordering_fields = ["created_at"]
