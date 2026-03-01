from django.urls import path
from .views import AnalyzeResumeView, RoleProfileListView

urlpatterns = [
    path('analyze-resume/', AnalyzeResumeView.as_view(), name='analyze-resume'),
    path('roles/', RoleProfileListView.as_view(), name='role-list'),
]
