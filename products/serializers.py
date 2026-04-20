from rest_framework import serializers
from .models import Product, Category, Color


# serializer for colors
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']


# serializer for categories
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'gender']


# product serializer (used for GET / read)
class ProductSerializer(serializers.ModelSerializer):
    # get category name directly
    category_name = serializers.CharField(source='category.name', read_only=True)

    # include full color objects
    colors = ColorSerializer(many=True, read_only=True)

    # custom field for image url
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'image',
            'category',
            'category_name',
            'gender',
            'sizes',
            'colors',
            'created_at',
        ]

    # return full image url (important for frontend)
    def get_image(self, obj):
        request = self.context.get('request')

        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url

        return None


# product serializer (used for POST/PUT)
class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'