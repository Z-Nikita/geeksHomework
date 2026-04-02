from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Category, Product, Review
from common.permissions import IsModerator, IsOwner, ReadOnly
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
    queryset = Product.objects.select_related("category", "owner").all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnly | IsOwner | IsModerator]

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            raise PermissionDenied('Moderator cannot create products.')
        serializer.save(owner=self.request.user)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("category", "owner").all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnly | IsOwner | IsModerator]
    lookup_field = "id"


class ProductReviewsListAPIView(generics.ListAPIView):
    queryset = (
        Product.objects.select_related("category", "owner")
        .prefetch_related("reviews")
        .annotate(rating=Coalesce(Avg("reviews__stars"), Value(0.0)))
        .all()
    )
    serializer_class = ProductWithReviewsSerializer


class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
