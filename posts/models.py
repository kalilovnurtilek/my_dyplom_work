# models.py

from django.db import models
from django.conf import settings

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('draft', 'Черновик'), ('published', 'Опубликован')], default='draft')
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def status_approval(self):
        if self.approval_steps.filter(is_approved=None).exists():
            return 'in_progress'
        elif self.approval_steps.filter(is_approved=False).exists():
            return 'rejected'
        elif self.approval_steps.filter(is_approved=True).exists():
            return 'approved'
        return 'not_started'

    @property
    def current_approver(self):
        step = self.approval_steps.filter(is_approved=None).order_by('order').first()
        return step.user if step else None

    class Meta:
        ordering = ['-created']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
class ApprovalStep(models.Model):
    post = models.ForeignKey(Post, related_name='approval_steps', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_approved = models.BooleanField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Этап {self.order}"

    
class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.text
