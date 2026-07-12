from django.db import models


class ProjectRequest(models.Model):
    CONTACT_METHODS = [
        ("email", "Email"),
        ("phone", "Phone"),
        ("whatsapp", "WhatsApp"),
        ("any", "Any"),
    ]

    name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=80, blank=True)
    company = models.CharField(max_length=140, blank=True)
    service = models.CharField(max_length=160, blank=True)
    services = models.JSONField(default=list, blank=True)
    book_title = models.CharField(max_length=180, blank=True)
    book_size = models.CharField(max_length=120, blank=True)
    page_count = models.CharField(max_length=80, blank=True)
    budget = models.CharField(max_length=120, blank=True)
    stage = models.CharField(max_length=160, blank=True)
    timeline = models.CharField(max_length=120, blank=True)
    referral_source = models.CharField(max_length=160, blank=True)
    preferred_contact_method = models.CharField(max_length=40, choices=CONTACT_METHODS, default="email")
    message = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    consent_to_contact = models.BooleanField(default=True)
    status = models.CharField(max_length=80, default="New")
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.service or 'Project request'}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=80, blank=True)
    reason = models.CharField(max_length=140, blank=True)
    subject = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=80, default="New")
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject or 'Contact message'}"


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=140, blank=True)
    source = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class TransportWaitlist(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=140, blank=True)
    phone = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=80, default="New")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
