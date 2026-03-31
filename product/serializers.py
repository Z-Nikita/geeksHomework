from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=255,
        error_messages={
            "blank": "Category name cannot be empty.",
            "required": "Category name is required.",
            "max_length": "Category name must be at most 255 characters long.",
        },
    )

    class Meta:
        model = Category
        fields = ("id", "name", "products_count")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Category name cannot contain only spaces.")

        queryset = Category.objects.filter(name__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={
            "required": "Category is required.",
            "does_not_exist": "Category does not exist.",
            "incorrect_type": "Category id must be a integer.",
            "null": "Category cannot be null.",
        },
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    title = serializers.CharField(
        max_length=255,
        error_messages={
            "blank": "Product title cannot be empty.",
            "required": "Product title is required.",
            "max_length": "Product title must be at most 255 characters long.",
        },
    )
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        error_messages={
            "required": "Price is required.",
            "invalid": "Price must be a valid number.",
            "max_digits": "Price must contain no more than 10 digits in total.",
            "max_decimal_places": "Price must contain no more than 2 decimal places.",
            "max_whole_digits": "Price is too large.",
        },
    )

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category", "category_name", "owner", "owner_email")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Product title cannot contain only spaces.")
        return value

    def validate_description(self, value):
        return value.strip()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        error_messages={
            "required": "Product is required.",
            "does_not_exist": "Product does not exist.",
            "incorrect_type": "Product id must be a integer.",
            "null": "Product cannot be null.",
        },
    )
    text = serializers.CharField(
        error_messages={
            "blank": "Review text cannot be empty.",
            "required": "Review text is required.",
        },
    )
    stars = serializers.IntegerField(
        min_value=1,
        max_value=5,
        error_messages={
            "required": "Stars value is required.",
            "invalid": "Stars must be an integer.",
            "min_value": "Stars must be at least 1.",
            "max_value": "Stars must be no more than 5.",
        },
    )

    class Meta:
        model = Review
        fields = ("id", "text", "stars", "product")

    def validate_text(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Review text cannot contain only spaces.")
        return value


class ReviewNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "text", "stars")


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
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
            "owner_email",
            "rating",
            "reviews",
        )
