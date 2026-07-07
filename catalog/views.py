from rest_framework import viewsets

from .models import Course, PortfolioProject, Product, Review, Service
from .serializers import CourseSerializer, PortfolioProjectSerializer, ProductSerializer, ReviewSerializer, ServiceSerializer


class PublicReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class ProductViewSet(PublicReadOnlyViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ["category"]
    search_fields = ["title", "subtitle", "summary", "author"]
    ordering_fields = ["display_order", "title", "price", "created_at"]


class CourseViewSet(PublicReadOnlyViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_fields = ["category", "status"]
    search_fields = ["title", "subtitle", "summary"]
    ordering_fields = ["display_order", "title", "price", "created_at"]


class PortfolioProjectViewSet(PublicReadOnlyViewSet):
    queryset = PortfolioProject.objects.all()
    serializer_class = PortfolioProjectSerializer
    filterset_fields = ["category", "featured"]
    search_fields = ["title", "summary", "client"]
    ordering_fields = ["display_order", "title", "created_at"]


class ServiceViewSet(PublicReadOnlyViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    search_fields = ["title", "summary"]
    ordering_fields = ["display_order", "title", "created_at"]


class ReviewViewSet(PublicReadOnlyViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    search_fields = ["title", "quote", "reviewer_name", "project"]
    ordering_fields = ["display_order", "rating", "created_at"]
