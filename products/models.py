import os
from django.db import models


SIZE_CHOICES = [
    ('XS',    'XS'),
    ('S',     'S'),
    ('M',     'M'),
    ('L',     'L'),
    ('XL',    'XL'),
    ('XXL',   'XXL'),
    ('3-4Y',  '3-4 Years'),
    ('5-6Y',  '5-6 Years'),
    ('7-8Y',  '7-8 Years'),
    ('9-10Y', '9-10 Years'),
]

GENDER_CHOICES = [
    ('men',    'Men'),
    ('women',  'Women'),
    ('kids',   'Kids'),
    ('unisex', 'Unisex'),
]


def product_image_path(instance, filename):
    return f'products/{filename}'


class Color(models.Model):
    name     = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    name        = models.CharField(max_length=255)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    image       = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True
    )
    is_active  = models.BooleanField(default=True)
    gender     = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unisex'
    )
    sizes  = models.JSONField(default=list, blank=True)
    colors = models.ManyToManyField(Color, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0

    # Returns the primary image object, or the first image.
    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            old = Product.objects.get(pk=self.pk)
            if old.image and old.image != self.image:
                if os.path.isfile(old.image.path):
                    os.remove(old.image.path)
        except Product.DoesNotExist:
            pass
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product    = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image      = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)
    order      = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Image for {self.product.name}'

    # When one image is set as primary, unset the others for the same product.
    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)