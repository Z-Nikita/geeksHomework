from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "products_count")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category", "category_name")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "text", "stars", "product")


class ReviewNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "text", "stars")


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    rating = serializers.FloatField(read_only=True)
    reviews = ReviewNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "price",
            "category",
            "category_name",
            "rating",
            "reviews",
        )
