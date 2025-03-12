from rest_framework import generics, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from notifications.models import Notification, NotificationSetting
from notifications.serializers import NotificationSerializer, NotificationSettingSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class NotificationListView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.notifications.all()
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class NotificationMarkReadView(APIView):
    """
    API endpoint for marking a notification as read.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    """
    API endpoint for marking all notifications as read.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({"status": "All notifications marked as read"})


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


class NotificationUnreadCountView(APIView):
    """
    API endpoint for getting the count of unread notifications.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count}) 