from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


# cart model (one cart per user)
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    # calculate total price of all items in cart
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


# single item inside cart
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size     = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # prevent duplicate same product + size in same cart
    class Meta:
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        size_display = f" ({self.size})" if self.size else ""
        return f"{self.quantity} × {self.product.name}{size_display}"

    # subtotal for this item
    @property
    def subtotal(self):
        return self.product.price * self.quantity


# order model
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    shipping_address = models.TextField()
    total_price      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} — {self.user.username} ({self.status})"


# items inside an order
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )
    size       = models.CharField(max_length=10, blank=True, null=True)
    quantity   = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        # handle case if product was deleted
        product_name = self.product.name if self.product else "Deleted Product"
        size_display = f" ({self.size})" if self.size else ""
        return f"{self.quantity} × {product_name}{size_display}"

    # subtotal for this order item
    @property
    def subtotal(self):
        return self.unit_price * self.quantity