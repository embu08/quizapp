from django.contrib import admin
from .models import *


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'category', 'owner')
    list_display_links = ('name',)
    search_fields = ('name', 'owner', 'description')
    list_filter = ('category', 'owner')
    readonly_fields = ('owner',)


class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer', 'test')
    list_display_links = ('question',)
    search_fields = ('question',)
    list_filter = ('test', )
    readonly_fields = ('test',)


class PassedTestsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test', 'grade', 'data_passed')
    list_display_links = ('user',)
    search_fields = ('test', 'user')
    list_filter = ('user', 'test', 'data_passed')
    readonly_fields = ('data_passed',)


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(PassedTests, PassedTestsAdmin)

# Register your models here.
