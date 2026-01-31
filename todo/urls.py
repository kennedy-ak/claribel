from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('create/', views.todo_create_view, name='create'),
    path('today/', views.todo_today_view, name='today'),
    path('toggle/<int:item_id>/', views.toggle_todo_item_view, name='toggle_item'),
    path('mentor/todos/', views.mentor_todos_view, name='mentor_todos'),
    path('mentor/todos/<int:todo_id>/', views.mentor_todo_detail_view, name='mentor_todo_detail'),
]
