from rest_framework import permissions, viewsets

from .models import BlogPost, Brand, Category, Course, PortfolioProject, Product, Review, Service
from .serializers import (
    BlogPostSerializer,
    BrandSerializer,
    CategorySerializer,
    CourseSerializer,
    PortfolioProjectSerializer,
    ProductSerializer,
    ReviewSerializer,
    ServiceSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class PublicContentViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(is_published=True)


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["category_type", "is_visible"]
    search_fields = ["name", "description"]
    ordering_fields = ["category_type", "display_order", "name", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user and self.request.user.is_staff:
            return queryset
        return queryset.filter(is_visible=True)


class ProductViewSet(PublicContentViewSet):
    queryset = Product.objects.select_related("category_ref")
    serializer_class = ProductSerializer
    filterset_fields = ["category", "category_ref", "featured", "is_digital"]
    search_fields = ["title", "subtitle", "summary", "author", "sku"]
    ordering_fields = ["display_order", "title", "price", "rating", "created_at"]


class CourseViewSet(PublicContentViewSet):
    queryset = Course.objects.select_related("category_ref")
    serializer_class = CourseSerializer
    filterset_fields = ["category", "category_ref", "status", "featured", "level"]
    search_fields = ["title", "subtitle", "summary"]
    ordering_fields = ["display_order", "title", "price", "created_at"]


class PortfolioProjectViewSet(PublicContentViewSet):
    queryset = PortfolioProject.objects.select_related("category_ref")
    serializer_class = PortfolioProjectSerializer
    filterset_fields = ["category", "category_ref", "featured", "service_type", "year"]
    search_fields = ["title", "summary", "client"]
    ordering_fields = ["display_order", "title", "created_at"]


class ServiceViewSet(PublicContentViewSet):
    queryset = Service.objects.select_related("category_ref")
    serializer_class = ServiceSerializer
    filterset_fields = ["category_ref", "availability"]
    search_fields = ["title", "summary", "starting_price", "price_range"]
    ordering_fields = ["display_order", "title", "created_at"]


class ReviewViewSet(PublicContentViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filterset_fields = ["service", "rating", "source", "featured"]
    search_fields = ["title", "quote", "reviewer_name", "project"]
    ordering_fields = ["display_order", "rating", "created_at"]


class BrandViewSet(PublicContentViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filterset_fields = ["status"]
    search_fields = ["title", "name", "summary", "code"]
    ordering_fields = ["display_order", "name", "created_at"]


class BlogPostViewSet(PublicContentViewSet):
    queryset = BlogPost.objects.select_related("category_ref")
    serializer_class = BlogPostSerializer
    filterset_fields = ["author", "category_ref"]
    search_fields = ["title", "excerpt", "content", "tags"]
    ordering_fields = ["display_order", "published_at", "created_at", "title"]
