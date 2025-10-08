from django.contrib import admin
from .models import MenuItem, Sale, SaleItem

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit_price', 'is_available', 'created_at']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale_date', 'total_amount', 'payment_method', 'created_by']
    list_filter = ['payment_method', 'sale_date', 'created_by']
    search_fields = ['notes']
    ordering = ['-sale_date']
    readonly_fields = ['total_amount']

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'menu_item', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['menu_item__category']
    search_fields = ['menu_item__name']
    ordering = ['sale']
    readonly_fields = ['subtotal']
