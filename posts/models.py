from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    created = models.DateTimeField(auto_now=True)
    