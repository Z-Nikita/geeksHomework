from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="products",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.title


class Review(models.Model):
    text = models.TextField()
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
        help_text="Rating from 1 to 5",
    )
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Review #{self.pk} for {self.product_id}"
