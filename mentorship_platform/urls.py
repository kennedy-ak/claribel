"""
URL configuration for mentorship_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('todo/', include('todo.urls')),
    path('reports/', include('reports.urls')),
    path('notifications/', include('notifications.urls')),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    # Direct dashboard access routes
    path('dashboard/mentor/', accounts_views.mentor_dashboard_view, name='mentor_dashboard_direct'),
    path('dashboard/mentee/', accounts_views.mentee_dashboard_view, name='mentee_dashboard_direct'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
