from django.urls import path
from notifications.views.notifications import (
    NotificationListView, NotificationMarkReadView,
    NotificationDeleteView, NotificationSettingView,
    NotificationUnreadCountView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('<int:pk>/', NotificationDeleteView.as_view(), name='notification-detail'),
    path('settings/', NotificationSettingView.as_view(), name='notification-settings'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
] 