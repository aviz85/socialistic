from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """
    Signal handler to send real-time notification via WebSocket when a notification is created.
    """
    if created:
        channel_layer = get_channel_layer()
        
        # Serialize the notification
        notification_data = NotificationSerializer(instance).data
        
        # Send to the recipient's notification group
        async_to_sync(channel_layer.group_send)(
            f'notifications_{instance.recipient.id}',
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        ) 