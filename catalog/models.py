from django.db import models
from django.utils.text import slugify


def unique_slug(instance, value):
    base_slug = slugify(value)[:200] or "item"
    slug = base_slug
    counter = 2
    model = instance.__class__

    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[: 220 - len(suffix)]}{suffix}"
        counter += 1

    return slug


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
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Category(TimestampedModel):
    CATEGORY_TYPES = [
        ("product", "Product"),
        ("course", "Course"),
        ("portfolio", "Portfolio"),
        ("blog", "Blog"),
        ("service", "Service"),
    ]

    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category_type = models.CharField(max_length=40, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["category_type", "display_order", "name"]
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category_type})"


class Product(PublishableModel):
    subtitle = models.CharField(max_length=220, blank=True)
    category = models.CharField(max_length=120, blank=True)
    category_ref = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="products")
    author = models.CharField(max_length=140, default="Danajet")
    sku = models.CharField(max_length=80, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    compare_at_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    amazon_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=0)
    inventory = models.PositiveIntegerField(default=0)
    age_range = models.CharField(max_length=80, blank=True)
    format = models.CharField(max_length=120, blank=True)
    featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    features = models.JSONField(default=list, blank=True)
    gallery = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)


class Course(PublishableModel):
    category = models.CharField(max_length=120, blank=True)
    category_ref = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="courses")
    subtitle = models.CharField(max_length=220, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=80, default="Coming Soon")
    video_url = models.URLField(blank=True)
    embed_url = models.URLField(blank=True)
    access_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    duration = models.CharField(max_length=80, blank=True)
    level = models.CharField(max_length=80, blank=True)
    featured = models.BooleanField(default=False)
    lessons = models.JSONField(default=list, blank=True)
    resources = models.JSONField(default=list, blank=True)
    outcomes = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)


class PortfolioProject(PublishableModel):
    category = models.CharField(max_length=120, blank=True)
    category_ref = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="portfolio_projects")
    client = models.CharField(max_length=180, blank=True)
    project_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    service_type = models.CharField(max_length=140, blank=True)
    year = models.CharField(max_length=20, blank=True)
    images = models.JSONField(default=list, blank=True)
    deliverables = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)


class Service(PublishableModel):
    icon = models.CharField(max_length=80, blank=True)
    starting_price = models.CharField(max_length=80, blank=True)
    category_ref = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="services")
    price_range = models.CharField(max_length=120, blank=True)
    duration = models.CharField(max_length=120, blank=True)
    request_url = models.CharField(max_length=220, default="/request-project")
    availability = models.CharField(max_length=80, default="Available")
    deliverables = models.JSONField(default=list, blank=True)
    process_steps = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)


class Review(PublishableModel):
    reviewer_name = models.CharField(max_length=140)
    reviewer_role = models.CharField(max_length=180, blank=True)
    reviewer_image = models.ImageField(upload_to="reviews/", blank=True, null=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    project = models.CharField(max_length=180, blank=True)
    service = models.CharField(max_length=120, blank=True)
    source = models.CharField(max_length=120, blank=True)
    cta_label = models.CharField(max_length=120, blank=True)
    cta_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)


class Brand(PublishableModel):
    title = models.CharField(max_length=180, blank=True)
    code = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=140)
    href = models.CharField(max_length=220, blank=True)
    icon = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=80, default="Visible")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta(PublishableModel.Meta):
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Danajet-{self.name}"
        super().save(*args, **kwargs)


class BlogPost(PublishableModel):
    excerpt = models.TextField(blank=True)
    author = models.CharField(max_length=140, default="Danajet")
    published_at = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True)
    tags = models.CharField(max_length=220, blank=True)
    category_ref = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="blog_posts")
    read_time = models.CharField(max_length=40, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
