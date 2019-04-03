from django.db import models
from chunked_upload.models import ChunkedUpload

# Create your models here.
class BookrDocument(models.Model):
    file = models.FileField(upload_to='media')

class BookrChunkedUpload(ChunkedUpload):
    pass
# Override the default ChunkedUpload to make the `user` field nullable
BookrChunkedUpload._meta.get_field('user').null = True