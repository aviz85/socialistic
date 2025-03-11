from django.urls import path
from projects.views.projects import (
    ProjectListCreateView, ProjectDetailView, ProjectCollaborateView,
    ProjectLeaveView, CollaborationRequestListView, CollaborationRequestResponseView
)

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/collaborate/', ProjectCollaborateView.as_view(), name='project-collaborate'),
    path('<int:pk>/leave/', ProjectLeaveView.as_view(), name='project-leave'),
    path('collaboration-requests/', CollaborationRequestListView.as_view(), name='collaboration-requests'),
    path('collaboration-requests/<int:pk>/respond/', CollaborationRequestResponseView.as_view(), name='collaboration-request-respond'),
] 