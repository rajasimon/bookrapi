from django.db import models

# Create your models here.
class BookrDocument(models.Model):
    file = models.FileField(upload_to='media')
