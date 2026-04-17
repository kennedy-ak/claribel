from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('create/', views.report_create_view, name='create'),
    path('today/', views.report_today_view, name='today'),
    path('<int:report_id>/edit/', views.report_edit_view, name='edit'),
    path('mentor/reports/', views.mentor_reports_view, name='mentor_reports'),
    path('mentor/reports/<int:report_id>/', views.mentor_report_detail_view, name='mentor_report_detail'),
]
