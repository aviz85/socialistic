from django.urls import path
from notifications.views.notifications import (
    NotificationListView, NotificationMarkReadView,
    NotificationDeleteView, NotificationSettingView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
    path('<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('settings/', NotificationSettingView.as_view(), name='notification-settings'),
] 