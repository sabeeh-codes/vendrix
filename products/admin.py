from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Color


# admin for colors
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['preview', 'name', 'hex_code']
    search_fields = ['name']

    # show color circle preview
    def preview(self, obj):
        return format_html(
            '<div style="width:24px;height:24px;border-radius:50%;background:{};border:1px solid #ddd;"></div>',
            obj.hex_code
        )
    preview.short_description = 'Color'


# admin for categories
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender']
    list_filter = ['gender']
    search_fields = ['name']
    ordering = ['name']


# admin for products
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'name', 'category',
        'gender', 'price', 'stock', 'is_active'
    ]

    # filters on right side
    list_filter = ['gender', 'category', 'is_active']

    # search by name or description
    search_fields = ['name', 'description']

    # allow editing directly in list view
    list_editable = ['price', 'stock', 'is_active']

    # better UI for many-to-many colors
    filter_horizontal = ['colors']

    # read-only fields
    readonly_fields = ['image_preview', 'created_at', 'updated_at']

    # group fields in admin form
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'gender')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Variants', {
            'fields': ('sizes', 'colors')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # show small image preview
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:6px;">',
                obj.image.url
            )
        return 'No Image'

    image_preview.short_description = 'Preview'