from django.db import models
from django.conf import settings

class Post(models.Model):
    title = models.CharField( max_length=300,verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created = models.DateTimeField(auto_now=True,verbose_name="Дата создание")
    status = models.BooleanField(default=True,verbose_name="Статус публикации")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ('-created',)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"



class Comment(models.Model):
    post = models.ForeignKey( Post, on_delete=models.CASCADE,related_name="post_comment",verbose_name="Пост")
    name = models.CharField(max_length=16,verbose_name="Имя пользователя")
    text = models.CharField(max_length=300,verbose_name="Текст комментария")
    created = models.DateTimeField(auto_now=True,verbose_name="Дата создания")
    
    def __str__(self):
        return f"{self.post.title}- {self.name}"
    
    class Meta:
        ordering = ('-created',)
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"



class PDFPost(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdfs/')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_pdfs')
    allowed_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='accessible_pdfs', blank=True)

    def __str__(self):
        return self.title
    