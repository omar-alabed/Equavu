"""
URL configuration for the HR application.
"""
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'equavo_hr_app'

urlpatterns = [
    # API test endpoint
    path('', views.APITestView.as_view(), name='api-test'),

    # Candidate endpoints
    path('candidates/register/', views.CandidateRegistrationView.as_view(), name='candidate-register'),
    path('candidates/<uuid:pk>/status/', views.CandidateStatusView.as_view(), name='candidate-status'),

    # Admin endpoints
    path('admin/candidates/', views.CandidateListView.as_view(), name='admin-candidate-list'),
    path('admin/candidates/<uuid:pk>/', views.CandidateDetailView.as_view(), name='admin-candidate-detail'),
    path('admin/candidates/<uuid:pk>/status/', views.StatusUpdateView.as_view(), name='admin-status-update'),
    path('admin/candidates/<uuid:pk>/resume/', views.ResumeDownloadView.as_view(), name='admin-resume-download'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
