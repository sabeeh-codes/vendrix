from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    color_name = serializers.SerializerMethodField()
    color_hex = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_detail',
            'size', 'color', 'color_name', 'color_hex',
            'quantity', 'subtotal',
        ]

    def get_color_name(self, obj):
        return obj.color.name if obj.color else None

    def get_color_hex(self, obj):
        return obj.color.hex_code if obj.color else None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    size = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)

    # support old and new frontend payloads
    color_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    color = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)

    def validate(self, data):
        color_id = data.get('color_id')
        color = data.get('color')

        if color_id is not None and color == '':
            data['color'] = None

        if color is not None and isinstance(color, str):
            data['color'] = color.strip() or None

        return data


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default='Deleted product')
    product_image = serializers.SerializerMethodField()
    color_name = serializers.SerializerMethodField()
    color_hex = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image',
            'size', 'color', 'color_name', 'color_hex',
            'quantity', 'unit_price', 'subtotal',
        ]

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product and obj.product.image:
            if request:
                return request.build_absolute_uri(obj.product.image.url)
            return 'http://127.0.0.1:8000' + obj.product.image.url
        return None

    def get_color_name(self, obj):
        return obj.color.name if obj.color else None

    def get_color_hex(self, obj):
        return obj.color.hex_code if obj.color else None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'shipping_address', 'total_price',
            'payment_method', 'payment_status',
            'stripe_payment_intent_id',
            'paid_at', 'items', 'created_at',
        ]
        read_only_fields = [
            'status', 'total_price', 'created_at',
            'payment_status', 'paid_at', 'stripe_payment_intent_id',
        ]


class PlaceOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=['cod', 'card'], default='cod')
    stripe_payment_intent_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)

    def validate(self, data):
        if data.get('payment_method') == 'card':
            if not data.get('stripe_payment_intent_id'):
                raise serializers.ValidationError({
                    'stripe_payment_intent_id': 'Payment intent ID is required for card payment.'
                })
        return data