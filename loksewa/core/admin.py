from django.contrib import admin
from .models import User, Note, Article, Pradesh, ModelSet, TemplateResource, GalleryImage, ContactMessage, Bookmark, Job, PradeshQA, CurrentEvent, SubjectiveSubject, SubjectiveChapter, SubjectiveQA, Category, ModelSetQuestion

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'sent_at', 'reply')
    search_fields = ('name', 'email', 'message')
    list_filter = ('sent_at',)
    readonly_fields = ('name', 'email', 'message', 'sent_at')
    fields = ('name', 'email', 'message', 'sent_at', 'reply')

admin.site.register(ContactMessage, ContactMessageAdmin)

admin.site.register(User)
admin.site.register(Note)
admin.site.register(Article)

class PradeshQAInline(admin.TabularInline):
    model = PradeshQA
    extra = 1

class PradeshAdmin(admin.ModelAdmin):
    list_display = ("province", "title", "document", "created_at")
    inlines = [PradeshQAInline]

admin.site.register(Pradesh, PradeshAdmin)
admin.site.register(PradeshQA)

admin.site.register(ModelSet)
admin.site.register(TemplateResource)
admin.site.register(GalleryImage)
admin.site.register(Bookmark)
admin.site.register(Job)
admin.site.register(CurrentEvent)
admin.site.register(SubjectiveSubject)
admin.site.register(SubjectiveChapter)
admin.site.register(SubjectiveQA)
admin.site.register(Category)
admin.site.register(ModelSetQuestion)

# Register your models here.
