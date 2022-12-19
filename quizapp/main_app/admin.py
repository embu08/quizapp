from .models import Categories, Test, Questions, PassedTests
from django.contrib import admin


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'category', 'owner', 'time_create', 'time_update')
    fields = ('name', 'description', 'category')
    list_display_links = ('name',)
    search_fields = ('name', 'owner', 'description', 'time_create')
    list_filter = ('category', 'owner', 'time_create')
    readonly_fields = ('owner', 'time_create', 'time_update')


class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer', 'test')
    list_display_links = ('question',)
    search_fields = ('question',)
    list_filter = ('test',)
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
