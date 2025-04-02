from django.contrib import admin
from posts.models import Post, Comment

# простой способ регистрации модели в админке
# admin.site.register(Post)




# Развернутый способ
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=["title", "created","status"]
    list_filter=["status",]
    list_editable = ["status",]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "name", "created"]