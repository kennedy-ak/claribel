from django import forms
from .models import TodoList, TodoItem


class TodoItemForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ['title', 'priority', 'status']


class TodoListForm(forms.ModelForm):
    class Meta:
        model = TodoList
        fields = ['is_submitted_to_mentor', 'mentor_notes']
