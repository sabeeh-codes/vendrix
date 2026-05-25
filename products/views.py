from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models    import Product, Category, Color
from .serializers import (
    ProductSerializer,
    ProductWriteSerializer,
    CategorySerializer,
    ColorSerializer,
)
from .filters import ProductFilter


class ColorViewSet(viewsets.ModelViewSet):
    queryset         = Color.objects.all()
    serializer_class = ColorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset         = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Filters:
      ?gender=men
      ?gender=women
      ?category=1            by id
      ?category_name=T-Shirt  by name
      ?gender=men&category_name=T-Shirt
      ?search=cotton
      ?ordering=price
      ?ordering=-created_at
      ?min_price=10&max_price=100
    """
    queryset = Product.objects.filter(
        is_active=True
    ).select_related(
        'category'
    ).prefetch_related(
        'colors',
        'images',
    ).order_by('-created_at')

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ProductFilter
    search_fields   = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name', 'stock']
    ordering        = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        return ProductSerializer

    def get_serializer_context(self):
        # Pass request so image URLs are absolute
        return {'request': self.request}

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]