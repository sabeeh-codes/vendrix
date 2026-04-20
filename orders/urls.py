from django.urls import path
from .views import (
    CartView, AddToCartView, RemoveFromCartView, ClearCartView,
    PlaceOrderView, MyOrdersView, OrderDetailView
)

urlpatterns = [
    # cart routes
    path('cart/',                      CartView.as_view(),          name='cart'),
    path('cart/add/',                  AddToCartView.as_view(),      name='cart-add'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='cart-remove'),
    path('cart/clear/',                ClearCartView.as_view(),      name='cart-clear'),

    # order routes
    path('orders/',                    MyOrdersView.as_view(),       name='my-orders'),
    path('orders/place/',              PlaceOrderView.as_view(),     name='place-order'),
    path('orders/<int:pk>/',           OrderDetailView.as_view(),    name='order-detail'),
]