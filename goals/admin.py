from django.contrib import admin

from goals.models import GoalComment, GoalCategory, Goal


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    readonly_fields = ('created', 'updated')
    list_filter = ['is_deleted']
    search_fields = ['title']


class GoalCommentInline(admin.StackedInline):
    model = GoalComment
    extra = 0


@admin.register(Goal)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ['title', 'description']
    readonly_fields = ('created', 'updated')
    list_filter = ['status', 'priority']
    inlines = [GoalCommentInline]

