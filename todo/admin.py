from django.contrib import admin
from .models import TodoList, TodoItem


class TodoItemInline(admin.TabularInline):
    model = TodoItem
    extra = 0
    fields = ['title', 'priority', 'status']


@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'submission_date', 'is_submitted_to_mentor', 'get_task_count']
    list_filter = ['submission_date', 'is_submitted_to_mentor']
    search_fields = ['mentee__username', 'mentee__email']
    date_hierarchy = 'submission_date'
    inlines = [TodoItemInline]

    def get_task_count(self, obj):
        return obj.tasks.count()
    get_task_count.short_description = 'Tasks'


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'todo_list', 'priority', 'status']
    list_filter = ['priority', 'status']
    search_fields = ['title', 'todo_list__mentee__username']
