from django.contrib import admin
from posts.models import Post , Specialty

# простой способ регистрации модели в админке
# admin.site.register(Post)

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name','code']
    list_filter = ['name']
    


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created', 'status', 'get_owner', 'get_pdf_link']
    list_filter = ['status', ]
    list_editable = ['status', ]

    def get_owner(self, obj):
        return obj.owner.email  # Используем email, так как это поле существует в модели CustomUser
    get_owner.short_description = 'Owner'

    def get_pdf_link(self, obj):
        if obj.pdf_file:
            return f'<a href="{obj.pdf_file.url}" target="_blank">PDF Link</a>'
        return 'No file'
    get_pdf_link.short_description = 'PDF File'
    get_pdf_link.allow_tags = True  # Это важно, чтобы HTML-ссылка рендерилась
# @admin.register(PDFPost)
# class PdfPostAdmin(admin.ModelAdmin):
#     list_display = ['title','owner','pdf_file']
#     list_filter= ['owner',]
#     list_editable = ['owner',]

# @admin.register(Post)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('text', 'author', 'created', 'post')  # Пример с корректными полями

# admin.site.register(Comment, CommentAdmin)