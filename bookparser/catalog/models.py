from django.db import models

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=255)

    def __str__(self):
        return self.author_name


class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    publisher_name = models.CharField(max_length=255)

    def __str__(self):
        return self.publisher_name
    
class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    gener_name = models.CharField(max_length=100)

    def __str__(self):
        return self.gener_name


class Book(models.Model):
    isbn = models.CharField(max_length=20, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(null=True,max_length=255)
    description = models.TextField(null=True,blank=True)
    weight = models.FloatField(null=True, blank=True)
    size = models.CharField(null=True,max_length=100, blank=True)
    age_limit = models.CharField(null=True, max_length=255, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    book_cover = models.CharField(null=True,max_length=255, blank=True)
    image_url = models.URLField(null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    author = models.ManyToManyField(
        Author,
        related_name='books'
    )
    publisher = models.ManyToManyField(
        Publisher,
        related_name='books'
    )
    genres = models.ManyToManyField(
        Genre,
        related_name='books'
    )

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class WebsourceBook(models.Model):
    book = models.ForeignKey(
        Book,
        to_field='isbn',
        on_delete=models.CASCADE
    )
    url = models.URLField()

    class Meta:
        db_table = "websource_book"
        unique_together = (('book', 'url'),)

    def __str__(self):
        return f"{self.book.isbn} → {self.url}"
    

