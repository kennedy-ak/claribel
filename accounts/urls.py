from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('mentor/dashboard/', views.mentor_dashboard_view, name='mentor_dashboard'),
    path('mentee/dashboard/', views.mentee_dashboard_view, name='mentee_dashboard'),

    # Organization management
    path('organization/create/', views.organization_create_view, name='organization_create'),
    path('organization/join/', views.organization_join_view, name='organization_join'),
    path('organization/<int:org_id>/', views.organization_detail_view, name='organization_detail'),
    path('organization/assign/<int:mentee_id>/', views.mentor_assign_view, name='mentor_assign'),
]
