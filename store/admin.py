from django.contrib import admin
from .models import Products
from .models import Category
from .models import Customer
from .models import ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty image fields to display

class ProductsAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'price', 'category', 'description')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

# Register your models here.
admin.site.register(Products, ProductsAdmin)
admin.site.register(Category)
admin.site.register(Customer)
