from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Notification(models.Model):
    """Notification model for user activities."""
    
    TYPE_CHOICES = [
        ('like', _('Like')),
        ('comment', _('Comment')),
        ('follow', _('Follow')),
        ('mention', _('Mention')),
        ('project_invite', _('Project Invitation')),
        ('project_request', _('Project Request')),
        ('project_accepted', _('Project Request Accepted')),
    ]
    
    # Who receives the notification
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    
    # Who triggered the notification
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_notifications',
        on_delete=models.CASCADE
    )
    
    # Type of notification
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    
    # Content (generic relation to any model)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional data
    text = models.CharField(_('text'), max_length=255)
    is_read = models.BooleanField(_('read'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.text}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]


class NotificationSetting(models.Model):
    """User preferences for notifications."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='notification_settings',
        on_delete=models.CASCADE
    )
    
    # Email notification preferences
    email_likes = models.BooleanField(default=True)
    email_comments = models.BooleanField(default=True)
    email_follows = models.BooleanField(default=True)
    email_mentions = models.BooleanField(default=True)
    email_project_invites = models.BooleanField(default=True)
    email_project_requests = models.BooleanField(default=True)
    
    # Push notification preferences
    push_likes = models.BooleanField(default=True)
    push_comments = models.BooleanField(default=True)
    push_follows = models.BooleanField(default=True)
    push_mentions = models.BooleanField(default=True)
    push_project_invites = models.BooleanField(default=True)
    push_project_requests = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notification settings for {self.user.username}"
