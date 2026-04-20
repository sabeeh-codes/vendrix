from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    AddToCartSerializer,
    OrderSerializer,
    PlaceOrderSerializer
)
from products.models import Product


# get current user's cart
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # create cart if it doesn't exist
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


# add item to cart
class AddToCartView(APIView):
    """
    POST /api/cart/add/
    Body: { product_id, quantity, size }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        size = serializer.validated_data.get('size')

        # get product or return 404
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # check if enough stock available
        if product.stock < quantity:
            return Response(
                {'error': f'Only {product.stock} items available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        # create or update cart item (product + size)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )

        # if already exists, just increase quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


# remove specific item from cart
class RemoveFromCartView(APIView):
    """
    DELETE /api/cart/remove/<product_id>/?size=M
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        size = request.query_params.get('size')

        cart = get_object_or_404(Cart, user=request.user)

        # find item using product + size
        item = get_object_or_404(
            CartItem,
            cart=cart,
            product_id=product_id,
            size=size
        )

        item.delete()

        return Response({'message': 'Item removed'}, status=status.HTTP_200_OK)


# clear all items from cart
class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)


# place order from cart
class PlaceOrderView(APIView):
    """
    POST /api/orders/place/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)

        # don't allow empty cart checkout
        if not cart.items.exists():
            return Response(
                {'error': 'Your cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            total_price=cart.total_price
        )

        # create order items from cart items
        for item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.size,  # include size
                quantity=item.quantity,
                unit_price=item.product.price
            )

            # reduce stock after order
            item.product.stock -= item.quantity
            item.product.save()

        # clear cart after placing order
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# get all orders of current user
class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items')


# get single order detail
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)