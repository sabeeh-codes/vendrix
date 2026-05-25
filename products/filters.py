import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Supported query params:

    ?gender=men                        men + unisex
    ?gender=women                      women + unisex
    ?gender=kids                       kids + unisex
    ?gender=unisex                     unisex only
    ?category=1                        by category ID
    ?category_name=T-Shirt             by category name (case-insensitive)
    ?min_price=10&max_price=100        price range
    ?in_stock=true                     only in-stock items
    ?gender=men&category_name=T-Shirt  combined
    """

    # Price range
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte'
    )

    # Category by ID: ?category=1
    category = django_filters.NumberFilter(
        field_name='category__id'
    )

    # Category by name: ?category_name=T-Shirt
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='iexact'
    )

    # Gender filter
    gender = django_filters.CharFilter(method='filter_gender')

    # Stock filter
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    def filter_gender(self, queryset, name, value):
        """
        Men / Women / Kids include Unisex too.
        Unisex shows only unisex products.
        """
        if not value or value.lower() == 'all':
            return queryset

        if value.lower() == 'unisex':
            return queryset.filter(gender='unisex')

        return queryset.filter(gender__in=[value.lower(), 'unisex'])

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    class Meta:
        model  = Product
        fields = [
            'is_active',
            'category',
            'category_name',
            'gender',
            'min_price',
            'max_price',
            'in_stock',
        ]