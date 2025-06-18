from django.contrib import admin
from posts.models import Post , Specialty, Subject, PostSubject, Curriculum, CurriculumSubject

# простой способ регистрации модели в админке
# admin.site.register(Post)

admin.site.register(Subject)
admin.site.register(PostSubject)

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


class CurriculumSubjectInline(admin.TabularInline):
    model = CurriculumSubject
    extra = 1

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('specialty', 'year', 'is_active')
    inlines = [CurriculumSubjectInline]