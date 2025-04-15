from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



class Post(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_posts')
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='allowed_posts')

    title = models.CharField(max_length=255)
    content = models.TextField()
    pdf_file = models.FileField(upload_to='pdfs/')
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')])

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class ApprovalStep(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='approval_steps')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    is_approved = models.BooleanField(null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user} — {self.post.title} — {self.order}"





class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    # если у вас нет поля 'name', вы можете использовать поле 'author' или другое.
    author = models.CharField(max_length=100)
    
    def __str__(self):
        return self.text

    