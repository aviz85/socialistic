from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from notifications.models import Notification, NotificationSetting
from notifications.serializers import NotificationSerializer, NotificationSettingSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class NotificationListView(generics.ListAPIView):
    """
    API endpoint for listing user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.notifications.all()


class NotificationMarkReadView(APIView):
    """
    API endpoint for marking a notification as read.
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)


class NotificationDeleteView(generics.DestroyAPIView):
    """
    API endpoint for deleting a notification.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.notifications.all()


class NotificationSettingView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating notification settings.
    """
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Get or create notification settings for the user
        settings, created = NotificationSetting.objects.get_or_create(user=self.request.user)
        return settings 