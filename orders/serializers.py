from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer


# serializer for each cart item
class CartItemSerializer(serializers.ModelSerializer):
    # include full product details (read only)
    product_detail = ProductSerializer(source='product', read_only=True)

    # subtotal for this item
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_detail',
            'size',
            'quantity',
            'subtotal',
        ]


# serializer for cart (with all items)
class CartSerializer(serializers.ModelSerializer):
    # nested items inside cart
    items = CartItemSerializer(many=True, read_only=True)

    # total cart price
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_price',
            'created_at',
        ]


# used when adding item to cart
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    # size is optional
    size = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


# serializer for order item
class OrderItemSerializer(serializers.ModelSerializer):
    # get product name directly
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    # subtotal for each order item
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'size',
            'quantity',
            'unit_price',
            'subtotal',
        ]


# serializer for full order
class OrderSerializer(serializers.ModelSerializer):
    # include all items in order
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'shipping_address',
            'total_price',
            'items',
            'created_at',
        ]

        # these fields should not be edited manually
        read_only_fields = [
            'status',
            'total_price',
            'created_at',
        ]


# used when placing order
class PlaceOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()