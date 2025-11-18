from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CoverType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Series(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    isbn = models.CharField(primary_key=True, max_length=20)
    title = models.CharField(max_length=255, null=True,)
    description = models.TextField(blank=True, null=True,)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    year = models.PositiveIntegerField(null=True)
    page_count = models.PositiveIntegerField(null=True)
    weight_grams = models.PositiveIntegerField(null=True,)
    size_mm = models.CharField(max_length=100, null=True,)  # Например: "210x145x30"
    age_limit = models.CharField(max_length=10, null=True,)  # Например: "12+"
    author = models.CharField(max_length=255, null=True,)
    

    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, null=True,)
 

    def __str__(self):
        return f"{self.title} ({self.isbn})"
    

