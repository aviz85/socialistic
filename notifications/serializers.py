from rest_framework import serializers
from .models import Notification, NotificationSetting
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'type', 'text',
            'is_read', 'created_at', 'content_type', 'object_id'
        ]
        read_only_fields = [
            'id', 'recipient', 'sender', 'type', 'text',
            'created_at', 'content_type', 'object_id'
        ]


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = [
            'email_likes', 'email_comments', 'email_follows',
            'email_mentions', 'email_project_invites', 'email_project_requests',
            'push_likes', 'push_comments', 'push_follows',
            'push_mentions', 'push_project_invites', 'push_project_requests'
        ] 