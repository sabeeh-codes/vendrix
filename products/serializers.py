import re
from rest_framework import serializers
from .models import Product, Category, Color, ProductImage


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Color
        fields = ['id', 'name', 'hex_code']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model  = ProductImage
        fields = ['id', 'image', 'is_primary', 'order']

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return f'http://127.0.0.1:8000{obj.image.url}'


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(
        source='products.count', read_only=True
    )

    class Meta:
        model  = Category
        fields = ['id', 'name', 'description', 'product_count']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='category.name', read_only=True
    )
    colors = ColorSerializer(many=True, read_only=True)
    image  = serializers.SerializerMethodField()
    sizes  = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock',
            'in_stock', 'image', 'images', 'category', 'category_name',
            'gender', 'sizes', 'colors', 'created_at',
        ]

    def get_image(self, obj):
        # Use primary gallery image first, then cover image
        request = self.context.get('request')

        primary = obj.images.filter(is_primary=True).first()
        if not primary:
            primary = obj.images.first()

        if primary and primary.image:
            if request:
                return request.build_absolute_uri(primary.image.url)
            return f'http://127.0.0.1:8000{primary.image.url}'

        # Fallback to product cover image
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f'http://127.0.0.1:8000{obj.image.url}'

        return None

    def get_images(self, obj):
        request = self.context.get('request')
        images  = obj.images.all().order_by('order')
        return ProductImageSerializer(
            images,
            many=True,
            context={'request': request}
        ).data

    def get_sizes(self, obj):
        sizes = obj.sizes
        if isinstance(sizes, list):
            return [str(s).strip() for s in sizes if str(s).strip()]
        if not sizes:
            return []
        sizes = str(sizes).strip()
        if not sizes:
            return []
        if ' ' in sizes:
            return [s.strip() for s in sizes.split() if s.strip()]
        if ',' in sizes:
            return [s.strip() for s in sizes.split(',') if s.strip()]
        kids = re.findall(r'\d+-\d+[Yy]', sizes)
        if kids:
            return kids
        standard = re.findall(r'XXL|XL|XS|XXS|[SML]', sizes)
        if standard:
            return standard
        numbers = re.findall(r'\d+', sizes)
        if numbers:
            return numbers
        return [sizes]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock',
            'image', 'category', 'gender', 'sizes', 'colors', 'is_active',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock cannot be negative.')
        return value