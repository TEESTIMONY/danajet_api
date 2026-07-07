from django.db import models
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublishableModel(TimestampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to="catalog/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["display_order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(PublishableModel):
    subtitle = models.CharField(max_length=220, blank=True)
    category = models.CharField(max_length=120, blank=True)
    author = models.CharField(max_length=140, default="Danajet")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    amazon_url = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)


class Course(PublishableModel):
    category = models.CharField(max_length=120, blank=True)
    subtitle = models.CharField(max_length=220, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=80, default="Coming Soon")
    video_url = models.URLField(blank=True)


class PortfolioProject(PublishableModel):
    category = models.CharField(max_length=120, blank=True)
    client = models.CharField(max_length=180, blank=True)
    project_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)


class Service(PublishableModel):
    icon = models.CharField(max_length=80, blank=True)
    starting_price = models.CharField(max_length=80, blank=True)


class Review(PublishableModel):
    reviewer_name = models.CharField(max_length=140)
    reviewer_role = models.CharField(max_length=180, blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    project = models.CharField(max_length=180, blank=True)
