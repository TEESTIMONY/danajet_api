from django.db import models


class ProjectRequest(models.Model):
    name = models.CharField(max_length=140)
    email = models.EmailField()
    service = models.CharField(max_length=160, blank=True)
    budget = models.CharField(max_length=120, blank=True)
    stage = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=80, default="New")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.service or 'Project request'}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=140)
    email = models.EmailField()
    subject = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject or 'Contact message'}"
