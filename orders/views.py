import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    OrderSerializer,
    PlaceOrderSerializer,
)
from products.models import Product, Color

stripe.api_key = settings.STRIPE_SECRET_KEY


def resolve_color_for_product(product, color_id=None, color_name=None):
    """
    Accept:
    - color_id from the frontend
    - color name from older frontend code
    """
    if color_id:
        color = get_object_or_404(Color, id=color_id)
        if not product.colors.filter(id=color.id).exists():
            raise ValueError('Selected color is not available for this product.')
        return color

    if color_name:
        color = product.colors.filter(name__iexact=color_name.strip()).first()
        if not color:
            raise ValueError('Selected color is not available for this product.')
        return color

    return None


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        size = serializer.validated_data.get('size') or None
        color_id = serializer.validated_data.get('color_id') or None
        color_name = serializer.validated_data.get('color') or None

        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Check stock
        already_in_cart = 0
        existing = CartItem.objects.filter(cart=cart, product=product).first()
        if existing:
            already_in_cart = existing.quantity

        if already_in_cart + quantity > product.stock:
            available = product.stock - already_in_cart
            if available <= 0:
                return Response(
                    {'error': f'You already have all {product.stock} available items in your cart.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': f'Only {available} more available. You already have {already_in_cart} in cart.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get color from color_id or color name
        color = None
        try:
            color = resolve_color_for_product(product, color_id=color_id, color_name=color_name)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            color=color,
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return Response(CartSerializer(cart).data)


class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        cart = get_object_or_404(Cart, user=request.user)
        size = request.query_params.get('size') or None
        color_id = request.query_params.get('color_id') or None
        color_name = request.query_params.get('color') or None

        qs = CartItem.objects.filter(cart=cart, product_id=product_id)
        if size:
            qs = qs.filter(size=size)

        if color_id:
            qs = qs.filter(color_id=color_id)
        elif color_name:
            qs = qs.filter(color__name__iexact=color_name)

        item = qs.first()
        if item:
            item.delete()
        return Response({'message': 'Item removed.'})


class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared.'})


class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)

        if not cart.items.exists():
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(cart.total_price * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                metadata={'user_id': str(request.user.id), 'user_email': request.user.email}
            )
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
        except stripe.error.StripeError as e:
            return Response({'error': str(e.user_message)}, status=status.HTTP_400_BAD_REQUEST)


class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)

        if not cart.items.exists():
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        for cart_item in cart.items.select_related('product'):
            if cart_item.quantity > cart_item.product.stock:
                return Response(
                    {'error': f'"{cart_item.product.name}" only has {cart_item.product.stock} left in stock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        payment_method = serializer.validated_data['payment_method']
        intent_id = serializer.validated_data.get('stripe_payment_intent_id')

        if payment_method == 'card':
            try:
                intent = stripe.PaymentIntent.retrieve(intent_id)
                if intent.status != 'succeeded':
                    return Response(
                        {'error': 'Payment not completed. Please try again.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                payment_status = 'paid'
                paid_at = timezone.now()
            except stripe.error.StripeError as e:
                return Response({'error': str(e.user_message)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            payment_status = 'unpaid'
            paid_at = None
            intent_id = None

        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            total_price=cart.total_price,
            payment_method=payment_method,
            payment_status=payment_status,
            stripe_payment_intent_id=intent_id,
            paid_at=paid_at,
            status='confirmed' if payment_status == 'paid' else 'pending',
        )

        for cart_item in cart.items.select_related('product', 'color'):
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                size=cart_item.size,
                color=cart_item.color,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
            )
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        cart.items.all().delete()

        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['shipped', 'delivered']:
            return Response({'error': 'Cannot cancel a shipped or delivered order.'}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == 'cancelled':
            return Response({'error': 'Order is already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        if order.payment_status == 'paid':
            return Response({'error': 'Paid orders cannot be cancelled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

        for item in order.items.select_related('product'):
            if item.product:
                item.product.stock += item.quantity
                item.product.save()

        order.status = 'cancelled'
        order.payment_status = 'failed'
        order.save()

        return Response({'message': f'Order #{order.id} cancelled. Stock restored.', 'order_id': order.id})


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product', 'items__color')

    def get_serializer_context(self):
        return {'request': self.request}


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}