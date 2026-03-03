from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
from rest_framework import generics
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductWithReviewsSerializer,
    ReviewSerializer,
)


# Categories
class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.annotate(products_count=Count("products", distinct=True)).all()
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.annotate(products_count=Count("products", distinct=True)).all()
    serializer_class = CategorySerializer
    lookup_field = "id"


# Products
class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    lookup_field = "id"


class ProductReviewsListAPIView(generics.ListAPIView):
    """List products with nested reviews + average rating (Avg stars)."""

    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("reviews")
        .annotate(rating=Coalesce(Avg("reviews__stars"), Value(0.0)))
        .all()
    )
    serializer_class = ProductWithReviewsSerializer


# Reviews
class ReviewListAPIView(generics.ListAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer


class ReviewDetailAPIView(generics.RetrieveAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer
    lookup_field = "id"
