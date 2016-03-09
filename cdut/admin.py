from django.contrib import admin

# Register your models here.
from cdut.models import Article, Content, File, Source, Type, VisitNum, Comment, User

admin.site.register(Article)
admin.site.register(Content)
admin.site.register(File)
admin.site.register(Source)
admin.site.register(Type)
admin.site.register(VisitNum)
admin.site.register(Comment)
admin.site.register(User)
