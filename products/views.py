from rest_framework import viewsets, permissions
from .models import Product, Category, Color
from .serializers import (
    ProductSerializer, ProductWriteSerializer,
    CategorySerializer, ColorSerializer
)
from .filters import ProductFilter


# viewset for colors
class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer

    # allow public read, admin for write
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


# viewset for categories
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # same permission logic as colors
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


# viewset for products
class ProductViewSet(viewsets.ModelViewSet):
    # only show active products + optimize queries
    queryset = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('colors')

    # filtering, searching and ordering options
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    # use different serializer for write operations
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        return ProductSerializer

    # pass request to serializer (needed for full image url)
    def get_serializer_context(self):
        return {'request': self.request}

    # public can view, only admin can modify
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]