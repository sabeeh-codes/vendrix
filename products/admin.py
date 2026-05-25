import re
import json

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from .models import Product, Category, Color, ProductImage


class SizesWidget(forms.TextInput):
    def format_value(self, value):
        if isinstance(value, list):
            return ', '.join(str(v) for v in value)
        if value and value not in ('[]', 'null', '""'):
            cleaned = value.strip('[]').replace('"', '').replace("'", '')
            return cleaned
        return ''

    def value_from_datadict(self, data, files, name):
        raw = data.get(name, '').strip()
        if raw:
            items = [s.strip() for s in re.split(r'[,\s]+', raw) if s.strip()]
            return json.dumps(items)
        return '[]'


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model   = Product
        fields  = '__all__'
        widgets = {
            'sizes': SizesWidget(attrs={
                'placeholder': 'S, M, L, XL  or  3-4Y, 5-6Y, 7-8Y',
                'style':       'width:400px;',
            }),
        }
        help_texts = {
            'sizes': (
                'Type sizes separated by commas. '
                'Adult: S, M, L, XL, XXL  |  '
                'Kids: 3-4Y, 5-6Y, 7-8Y, 9-10Y'
            ),
        }


class ProductImageInline(admin.TabularInline):
    model           = ProductImage
    extra           = 2
    fields          = ['image', 'image_preview', 'is_primary', 'order']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80"'
                ' style="object-fit:cover;border-radius:6px;"/>',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form    = ProductAdminForm
    inlines = [ProductImageInline]

    list_display = [
        'image_thumb',
        'name',
        'category',
        'gender',
        'sizes_display',
        'color_swatches',
        'price',
        'stock',
        'is_active',
        'created_at',
        'delete_link',
    ]
    list_filter   = ['gender', 'category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
    actions       = ['delete_selected']

    # Removed Cover Image fieldset. Images are managed through the inline only.
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'gender')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Variants', {
            'description': (
                'Sizes: type comma-separated e.g. S, M, L, XL. '
                'Colors: select from the list on the right.'
            ),
            'fields': ('sizes', 'colors'),
        }),
    )

    filter_horizontal = ['colors']

    def image_thumb(self, obj):
        # Use primary_image instead of obj.image
        primary = obj.primary_image
        if primary:
            return format_html(
                '<img src="{}" width="44" height="44"'
                ' style="object-fit:cover;border-radius:6px;'
                'border:1px solid #eee;"/>',
                primary.image.url
            )
        return format_html(
            '<div style="width:44px;height:44px;border-radius:6px;'
            'background:#f5f5f5;display:flex;align-items:center;'
            'justify-content:center;font-size:18px;">👕</div>'
        )
    image_thumb.short_description = ''

    def sizes_display(self, obj):
        sizes = obj.sizes
        if not sizes:
            return '—'
        if isinstance(sizes, str):
            sizes = re.findall(r'\d+-\d+Y|XXL|XL|XS|[SML]|\d+', sizes)
        if not sizes:
            return '—'
        tags = ''.join(
            '<span style="display:inline-block;background:#f1f5f9;'
            'border:1px solid #e2e8f0;border-radius:4px;'
            'padding:1px 6px;font-size:11px;margin:1px;">'
            + str(s) + '</span>'
            for s in sizes
        )
        return mark_safe(tags)
    sizes_display.short_description = 'Sizes'

    def color_swatches(self, obj):
        swatches = [
            format_html(
                '<div title="{}" style="display:inline-block;'
                'width:16px;height:16px;border-radius:50%;'
                'background:{};border:1px solid #ddd;'
                'margin-right:2px;vertical-align:middle;"></div>',
                color.name, color.hex_code
            )
            for color in obj.colors.all()
            if color.hex_code
        ]
        return mark_safe(''.join(swatches)) if swatches else '—'
    color_swatches.short_description = 'Colors'

    def delete_link(self, obj):
        url = reverse('admin:products_product_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" style="'
            'color:#fff;background:#e94560;'
            'padding:4px 10px;border-radius:6px;'
            'font-size:12px;font-weight:700;'
            'text-decoration:none;">'
            '🗑 Delete'
            '</a>',
            url
        )
    delete_link.short_description = 'Action'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'description', 'product_count', 'delete_link']
    search_fields = ['name']
    actions       = ['delete_selected']

    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="font-weight:600;">{}</span> products',
            count
        )
    product_count.short_description = 'Products'

    def delete_link(self, obj):
        url = reverse('admin:products_category_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" style="color:#fff;background:#e94560;'
            'padding:4px 10px;border-radius:6px;'
            'font-size:12px;font-weight:700;text-decoration:none;">'
            '🗑 Delete</a>',
            url
        )
    delete_link.short_description = ''


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display  = ['color_preview', 'name', 'hex_code', 'delete_link']
    search_fields = ['name']
    actions       = ['delete_selected']

    def color_preview(self, obj):
        return format_html(
            '<div style="width:28px;height:28px;border-radius:50%;'
            'background:{};border:1px solid #ddd;"></div>',
            obj.hex_code
        )
    color_preview.short_description = ''

    def delete_link(self, obj):
        url = reverse('admin:products_color_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" style="color:#fff;background:#e94560;'
            'padding:4px 10px;border-radius:6px;'
            'font-size:12px;font-weight:700;text-decoration:none;">'
            'Delete</a>',
            url
        )
    delete_link.short_description = ''


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display  = ['product', 'is_primary', 'order', 'image_preview']
    list_filter   = ['is_primary']
    ordering      = ['product', 'order']
    actions       = ['delete_selected']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60"'
                ' style="object-fit:cover;border-radius:4px;"/>',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'