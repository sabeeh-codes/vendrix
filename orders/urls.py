from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    RemoveFromCartView,
    ClearCartView,
    CreatePaymentIntentView,
    PlaceOrderView,
    CancelOrderView,
    MyOrdersView,
    OrderDetailView,
)

urlpatterns = [
    # Cart
    path('cart/',                         CartView.as_view(),                name='cart'),
    path('cart/add/',                     AddToCartView.as_view(),            name='cart-add'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(),       name='cart-remove'),
    path('cart/clear/',                   ClearCartView.as_view(),            name='cart-clear'),

    # Stripe
    path('orders/create-payment-intent/', CreatePaymentIntentView.as_view(),  name='create-payment-intent'),

    # Orders
    path('orders/',                       MyOrdersView.as_view(),             name='my-orders'),
    path('orders/place/',                 PlaceOrderView.as_view(),           name='place-order'),
    path('orders/<int:pk>/',              OrderDetailView.as_view(),          name='order-detail'),
    path('orders/<int:order_id>/cancel/', CancelOrderView.as_view(),          name='cancel-order'),
]