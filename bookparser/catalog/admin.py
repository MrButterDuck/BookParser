from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django import forms
from .models import (
    Book, Publisher, Author, WebsourceBook, Genre
)

@admin.register(Book)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("isbn", "title", "price", "author_names", 'publisher_names', "genre_names", "created_at",)
    list_filter = ("publisher", "price", "created_at")
    search_fields = ("isbn", "title")
    ordering = ("created_at",)

    def author_names(self, obj):
        return ", ".join([a.author_name for a in obj.author.all()]) if obj.author.exists() else "—"
    author_names.short_description = "Author"

    def publisher_names(self, obj):
        return ", ".join([p.publisher_name for p in obj.publisher.all()]) if obj.publisher.exists() else "—"
    publisher_names.short_description = "Publisher"

    def genre_names(self, obj):
        return ", ".join([p.gener_name for p in obj.genres.all()]) if obj.genres.exists() else "—"
    publisher_names.short_description = "Genres"


admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(WebsourceBook)

