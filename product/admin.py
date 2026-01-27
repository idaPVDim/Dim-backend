from django.contrib import admin
from .models import Product, Category, Brand

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'is_active')
    list_filter = ('category', 'brand', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin): 
    list_display = ('name', 'country')
    search_fields = ('name',)
    ordering = ('name',)
    