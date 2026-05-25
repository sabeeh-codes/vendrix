from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model           = CartItem
    extra           = 0
    fields          = ['product', 'size', 'color', 'quantity', 'subtotal_display']
    readonly_fields = ['subtotal_display']

    def subtotal_display(self, obj):
        try:
            return '${:,.2f}'.format(float(obj.subtotal))
        except Exception:
            return '$0.00'
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ['user', 'item_count', 'total_display', 'created_at']
    search_fields = ['user__username', 'user__email']
    inlines       = [CartItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

    def total_display(self, obj):
        try:
            return '${:,.2f}'.format(float(obj.total_price))
        except Exception:
            return '$0.00'
    total_display.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    model      = OrderItem
    extra      = 0
    can_delete = False

    # Readonly fields only
    fields = [
        'product_name_display',
        'size_display',
        'color_display',
        'quantity',
        'unit_price',
        'line_total',
    ]
    readonly_fields = [
        'product_name_display',
        'size_display',
        'color_display',
        'quantity',
        'unit_price',
        'line_total',
    ]

    def product_name_display(self, obj):
        if obj.product:
            return obj.product.name
        return '—'
    product_name_display.short_description = 'Product'

    def size_display(self, obj):
        if obj.size:
            return format_html(
                '<span style="background:#f0f0f0;padding:2px 8px;'
                'border-radius:4px;font-weight:700;font-size:12px;">{}</span>',
                obj.size
            )
        return '—'
    size_display.short_description = 'Size'

    def color_display(self, obj):
        if obj.color and obj.color.hex_code:
            return format_html(
                '<div style="display:flex;align-items:center;gap:6px;">'
                '<div style="width:18px;height:18px;border-radius:50%;'
                'background:{};border:1.5px solid #ccc;flex-shrink:0;"></div>'
                '<span style="font-size:12px;font-weight:600;">{}</span>'
                '</div>',
                obj.color.hex_code,
                obj.color.name,
            )
        return '—'
    color_display.short_description = 'Color'

    def line_total(self, obj):
        try:
            total = float(obj.unit_price or 0) * (obj.quantity or 0)
            return '${:,.2f}'.format(total)
        except Exception:
            return '$0.00'
    line_total.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id',
        'customer_info',
        'order_status_badge',
        'payment_method_badge',
        'payment_status_badge',
        'items_summary',
        'color_swatches',
        'total_bill',
        'shipping_preview',
        'created_at',
    ]
    list_filter   = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'shipping_address']
    inlines       = [OrderItemInline]

    # Only status is editable
    readonly_fields = [
        'user', 'shipping_address', 'total_price',
        'payment_method', 'payment_status',
        'stripe_payment_intent_id', 'paid_at',
        'created_at', 'updated_at',
    ]

    fieldsets = (
        ('Order Status', {
            'fields': ('status',),
            'description': 'Only the status field can be changed by admin.',
        }),
        ('Order Details', {
            'fields': ('user', 'shipping_address', 'total_price'),
        }),
        ('Payment', {
            'fields': (
                'payment_method', 'payment_status',
                'stripe_payment_intent_id', 'paid_at',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    def mark_confirmed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} order(s) marked as confirmed.')
    mark_confirmed.short_description = 'Mark selected as Confirmed'

    def mark_shipped(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_shipped.short_description = 'Mark selected as Shipped'

    def mark_delivered(self, request, queryset):
        updated = queryset.filter(status='shipped').update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_delivered.short_description = 'Mark selected as Delivered'

    def mark_cancelled(self, request, queryset):
        for order in queryset.filter(status__in=['pending', 'confirmed']):
            for item in order.items.select_related('product'):
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
            order.status = 'cancelled'
            order.save()
        self.message_user(request, 'Orders cancelled and stock restored.')
    mark_cancelled.short_description = 'Cancel selected (restore stock)'

    def order_id(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    order_id.short_description = 'Order'
    order_id.admin_order_field = 'id'

    def customer_info(self, obj):
        return format_html(
            '<strong>{}</strong><br>'
            '<span style="color:#666;font-size:11px;">{}</span>',
            obj.user.username, obj.user.email,
        )
    customer_info.short_description = 'Customer'

    def order_status_badge(self, obj):
        colors = {
            'pending':   ('#fff3cd', '#856404'),
            'confirmed': ('#cce5ff', '#004085'),
            'shipped':   ('#d1ecf1', '#0c5460'),
            'delivered': ('#d4edda', '#155724'),
            'cancelled': ('#f8d7da', '#721c24'),
        }
        bg, text = colors.get(obj.status, ('#eee', '#333'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;">{}</span>',
            bg, text, obj.status.upper()
        )
    order_status_badge.short_description = 'Status'

    def payment_method_badge(self, obj):
        method = obj.payment_method or 'cod'
        if method == 'card':
            bg, text, label = '#e8eaf6', '#1a237e', 'Card'
        else:
            bg, text, label = '#fff3cd', '#856404', 'COD'
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;">{}</span>',
            bg, text, label
        )
    payment_method_badge.short_description = 'Method'

    def payment_status_badge(self, obj):
        options = {
            'unpaid': ('#f8d7da', '#721c24', 'Unpaid'),
            'paid':   ('#d4edda', '#155724', 'Paid'),
            'failed': ('#f8d7da', '#721c24', 'Failed'),
        }
        bg, text, label = options.get(obj.payment_status, ('#eee', '#333', obj.payment_status))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;">{}</span>',
            bg, text, label
        )
    payment_status_badge.short_description = 'Payment'

    def items_summary(self, obj):
        lines = []
        for item in obj.items.select_related('product').all():
            name = item.product.name if item.product else 'Deleted'
            size = ' ({})'.format(item.size) if item.size else ''
            lines.append(format_html(
                '<div style="font-size:12px;line-height:1.6;">'
                '• {} <em style="color:#888;">{}</em> × {}'
                '</div>',
                name, size, item.quantity
            ))
        return mark_safe(''.join(lines)) if lines else '—'
    items_summary.short_description = 'Products'

    def color_swatches(self, obj):
        swatches = []
        for item in obj.items.select_related('color').all():
            if item.color and item.color.hex_code:
                swatches.append(format_html(
                    '<div title="{}" style="display:inline-block;width:18px;'
                    'height:18px;border-radius:50%;background:{};'
                    'border:1px solid #ccc;margin-right:3px;'
                    'vertical-align:middle;"></div>',
                    item.color.name, item.color.hex_code,
                ))
        return mark_safe(' '.join(swatches)) if swatches else '—'
    color_swatches.short_description = 'Colors'

    def total_bill(self, obj):
        return format_html(
            '<strong style="color:#e94560;">{}</strong>',
            '${:,.2f}'.format(float(obj.total_price))
        )
    total_bill.short_description = 'Total'
    total_bill.admin_order_field = 'total_price'

    def shipping_preview(self, obj):
        addr  = obj.shipping_address or '—'
        short = addr if len(addr) <= 35 else addr[:35] + '…'
        return format_html(
            '<span title="{}" style="font-size:12px;color:#555;">{}</span>',
            addr, short
        )
    shipping_preview.short_description = 'Ship To'