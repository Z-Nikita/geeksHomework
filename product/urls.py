from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path("categories/", views.CategoryListAPIView.as_view(), name="category-list"),
    path("categories/<int:id>/", views.CategoryDetailAPIView.as_view(), name="category-detail"),

    # Products
    path("products/", views.ProductListAPIView.as_view(), name="product-list"),
    path("products/reviews/", views.ProductReviewsListAPIView.as_view(), name="product-reviews"),
    path("products/<int:id>/", views.ProductDetailAPIView.as_view(), name="product-detail"),

    # Reviews
    path("reviews/", views.ReviewListAPIView.as_view(), name="review-list"),
    path("reviews/<int:id>/", views.ReviewDetailAPIView.as_view(), name="review-detail"),
]
