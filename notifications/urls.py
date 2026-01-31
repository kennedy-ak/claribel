from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('start/<str:username>/', views.conversation_start_view, name='conversation_start'),

    # Legacy URLs - kept for backwards compatibility
    path('send/<str:username>/', views.message_send_view, name='send'),
    path('message/<int:message_id>/', views.message_detail_view, name='message_detail'),
]
