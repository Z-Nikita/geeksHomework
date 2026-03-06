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


class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count("products", distinct=True)).all()
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(products_count=Count("products", distinct=True)).all()
    serializer_class = CategorySerializer
    lookup_field = "id"


class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    lookup_field = "id"


class ProductReviewsListAPIView(generics.ListAPIView):
    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("reviews")
        .annotate(rating=Coalesce(Avg("reviews__stars"), Value(0.0)))
        .all()
    )
    serializer_class = ProductWithReviewsSerializer


class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer
    lookup_field = "id"
