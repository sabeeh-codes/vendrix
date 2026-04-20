from django.db import models


# size options for products
SIZE_CHOICES = [
    ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
    ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
    ('3-4Y', '3-4 Years'), ('5-6Y', '5-6 Years'),
    ('7-8Y', '7-8 Years'), ('9-10Y', '9-10 Years'),
]

# gender categories for filtering
GENDER_CHOICES = [
    ('men', 'Men'),
    ('women', 'Women'),
    ('kids', 'Kids'),
    ('unisex', 'Unisex'),
]


# decide where product images will be saved
def product_image_path(instance, filename):
    return f'products/{instance.gender}/{filename}'


# model for colors (like red, blue etc)
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name


# product category model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # category can be linked to gender
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unisex'
    )

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name   # just return name for display


# main product model
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products'
    )

    name = models.CharField(max_length=255)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    # optional product image
    image = models.ImageField(
        upload_to=product_image_path,
        blank=True,
        null=True
    )

    # whether product is visible or not
    is_active = models.BooleanField(default=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unisex'
    )

    # store sizes as list (json)
    sizes = models.JSONField(
        default=list,
        blank=True,
        help_text='Example: ["S", "M", "L"]'
    )

    # multiple colors allowed
    colors = models.ManyToManyField(Color, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # check if product is in stock
    @property
    def in_stock(self):
        return self.stock > 0