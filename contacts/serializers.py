from rest_framework import serializers

from .models import ContactMessage, NewsletterSubscription, ProjectRequest, TransportWaitlist


class ProjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRequest
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TransportWaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportWaitlist
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]
