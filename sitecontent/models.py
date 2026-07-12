from django.db import models
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def unique_slug(instance, value):
    base_slug = slugify(value)[:180] or "item"
    slug = base_slug
    counter = 2
    model = instance.__class__

    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[: 220 - len(suffix)]}{suffix}"
        counter += 1

    return slug


class SiteSetting(TimestampedModel):
    key = models.SlugField(max_length=120, unique=True)
    label = models.CharField(max_length=160)
    value = models.TextField(blank=True)
    value_json = models.JSONField(default=dict, blank=True)
    group = models.CharField(max_length=80, default="general")
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["group", "key"]

    def __str__(self):
        return self.label


class NavigationItem(TimestampedModel):
    NAVIGATION_AREAS = [
        ("header", "Header"),
        ("footer", "Footer"),
        ("mobile", "Mobile"),
        ("admin", "Admin"),
    ]

    label = models.CharField(max_length=120)
    href = models.CharField(max_length=240)
    area = models.CharField(max_length=40, choices=NAVIGATION_AREAS, default="header")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="children")
    icon = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    opens_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ["area", "display_order", "label"]

    def __str__(self):
        return f"{self.area}: {self.label}"


class PageSection(TimestampedModel):
    PAGE_CHOICES = [
        ("home", "Home"),
        ("about", "About"),
        ("portfolio", "Portfolio"),
        ("shop", "Shop"),
        ("courses", "Courses"),
        ("reviews", "Reviews"),
        ("contact", "Contact"),
        ("request-project", "Request Project"),
        ("transport", "Transport"),
    ]

    page = models.CharField(max_length=80, choices=PAGE_CHOICES)
    section_key = models.SlugField(max_length=120)
    eyebrow = models.CharField(max_length=160, blank=True)
    title = models.CharField(max_length=220, blank=True)
    subtitle = models.TextField(blank=True)
    body = models.TextField(blank=True)
    media = models.ForeignKey("MediaAsset", on_delete=models.SET_NULL, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["page", "display_order", "section_key"]
        unique_together = ["page", "section_key"]

    def __str__(self):
        return f"{self.page}: {self.section_key}"


class CallToAction(TimestampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    copy = models.TextField(blank=True)
    button_label = models.CharField(max_length=120)
    button_url = models.CharField(max_length=240)
    location = models.CharField(max_length=160, blank=True)
    style = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class MediaAsset(TimestampedModel):
    ASSET_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("pdf", "PDF"),
        ("document", "Document"),
        ("folder", "Folder"),
        ("external", "External URL"),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    asset_type = models.CharField(max_length=40, choices=ASSET_TYPES, default="image")
    file = models.FileField(upload_to="uploads/", blank=True, null=True)
    external_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=220, blank=True)
    usage = models.CharField(max_length=180, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["asset_type", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SocialLink(TimestampedModel):
    platform = models.CharField(max_length=80)
    url = models.CharField(max_length=240)
    icon = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "platform"]

    def __str__(self):
        return self.platform


class RequestFormOptionSet(TimestampedModel):
    key = models.SlugField(max_length=120, unique=True)
    label = models.CharField(max_length=160)
    options = models.JSONField(default=list, blank=True)
    helper_text = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "label"]

    def __str__(self):
        return self.label
