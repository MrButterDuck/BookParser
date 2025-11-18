from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django import forms
from .models import (
    Product, Publisher, CoverType, Series, ProductType
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("isbn", "title", "price", "year", "publisher",)
    list_filter = ("publisher", "year")
    search_fields = ("isbn", "title")
    ordering = ("title",)


admin.site.register(Publisher)
admin.site.register(CoverType)
admin.site.register(Series)
admin.site.register(ProductType)

