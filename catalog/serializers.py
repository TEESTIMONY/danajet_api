from rest_framework import serializers

from .models import BlogPost, Brand, Category, Course, PortfolioProject, Product, Review, Service


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category_ref", read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value


class CourseSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category_ref", read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


class PortfolioProjectSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category_ref", read_only=True)

    class Meta:
        model = PortfolioProject
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category_ref", read_only=True)

    class Meta:
        model = Service
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class BlogPostSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category_ref", read_only=True)

    class Meta:
        model = BlogPost
        fields = "__all__"
