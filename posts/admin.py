from django.contrib import admin
from posts.models import Post

# простой способ регистрации модели в админке
# admin.site.register(Post)




# Развернутый способ
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display=["title", "created","status"]
    list_filter=["status",]
    list_editable = ["status",]