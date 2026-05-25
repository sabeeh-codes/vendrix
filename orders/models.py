from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, Color

User = get_user_model()


class Cart(models.Model):
    user       = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart     = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items'
    )
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    size     = models.CharField(max_length=10, blank=True, null=True)
    color    = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product', 'size', 'color')

    def __str__(self):
        size_str  = f" ({self.size})"       if self.size  else ""
        color_str = f" - {self.color.name}" if self.color else ""
        return f"{self.quantity} x {self.product.name}{size_str}{color_str}"

    @property
    def subtotal(self):
        if not self.product or self.product.price is None:
            return 0
        return self.product.price * (self.quantity or 0)


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped',   'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod',  'Cash on Delivery'),
        ('card', 'Credit / Debit Card'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid',  'Unpaid'),
        ('paid',    'Paid'),
        ('failed',  'Failed'),
    ]

    user             = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders'
    )
    status           = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    shipping_address = models.TextField()
    total_price      = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )

    # Stripe
    stripe_payment_intent_id = models.CharField(
        max_length=200, blank=True, null=True,
        help_text='Stripe PaymentIntent ID'
    )
    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.status})"


class OrderItem(models.Model):
    order      = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    product    = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True
    )
    size       = models.CharField(max_length=10, blank=True, null=True)
    color      = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    def __str__(self):
        name = self.product.name if self.product else "Deleted Product"
        return f"{self.quantity} x {name}"

    @property
    def subtotal(self):
        return (self.unit_price or 0) * (self.quantity or 0)