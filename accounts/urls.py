from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('mentor/dashboard/', views.mentor_dashboard_view, name='mentor_dashboard'),
    path('mentee/dashboard/', views.mentee_dashboard_view, name='mentee_dashboard'),

    # Organization management
    path('organization/create/', views.organization_create_view, name='organization_create'),
    path('organization/join/', views.organization_join_view, name='organization_join'),
    path('organization/<int:org_id>/', views.organization_detail_view, name='organization_detail'),
    path('organization/<int:org_id>/edit/', views.organization_update_view, name='organization_edit'),
    path('organization/assign/<int:mentee_id>/', views.mentor_assign_view, name='mentor_assign'),

    # Task management
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/', views.task_list_view, name='task_list'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:task_id>/update/', views.task_update_view, name='task_update'),
    path('tasks/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),

    # Meeting management
    path('meetings/create/', views.meeting_create_view, name='meeting_create'),
    path('meetings/', views.meeting_list_view, name='meeting_list'),
    path('meetings/<int:meeting_id>/', views.meeting_detail_view, name='meeting_detail'),
    path('meetings/<int:meeting_id>/update/', views.meeting_update_view, name='meeting_update'),
    path('meetings/<int:meeting_id>/cancel/', views.meeting_cancel_view, name='meeting_cancel'),
]
