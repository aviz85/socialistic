import pytest
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from tests.factories import UserFactory, PostFactory, CommentFactory, NotificationFactory

pytestmark = pytest.mark.django_db


class TestNotificationModel:
    """Unit tests for the Notification model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_notification_creation(self, user, another_user):
        """Test creating a notification."""
        post = PostFactory(author=user)
        content_type = ContentType.objects.get_for_model(post)
        
        notification = Notification.objects.create(
            recipient=user,
            sender=another_user,
            notification_type='post_like',
            content_type=content_type,
            object_id=post.id,
            text=f"{another_user.username} liked your post"
        )
        
        assert notification.recipient == user
        assert notification.sender == another_user
        assert notification.notification_type == 'post_like'
        assert notification.content_type == content_type
        assert notification.object_id == post.id
        assert notification.text == f"{another_user.username} liked your post"
        assert notification.read is False
        assert notification.created_at <= timezone.now()

    @pytest.mark.unit
    @pytest.mark.model
    def test_notification_str(self, user, another_user):
        """Test the string representation of a notification."""
        notification = NotificationFactory(
            recipient=user,
            sender=another_user,
            notification_type='post_like',
            text=f"{another_user.username} liked your post"
        )
        
        expected_str = f"Notification from {another_user.username} to {user.username}: {notification.text}"
        assert str(notification) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_mark_as_read(self, user, another_user):
        """Test marking a notification as read."""
        notification = NotificationFactory(
            recipient=user,
            sender=another_user,
            notification_type='post_like',
            text=f"{another_user.username} liked your post",
            read=False
        )
        
        notification.mark_as_read()
        
        # Check that the notification was marked as read
        assert notification.read is True

    @pytest.mark.unit
    @pytest.mark.model
    def test_mark_as_unread(self, user, another_user):
        """Test marking a notification as unread."""
        notification = NotificationFactory(
            recipient=user,
            sender=another_user,
            notification_type='post_like',
            text=f"{another_user.username} liked your post",
            read=True
        )
        
        notification.mark_as_unread()
        
        # Check that the notification was marked as unread
        assert notification.read is False

    @pytest.mark.unit
    @pytest.mark.model
    def test_get_related_object(self, user, another_user):
        """Test getting the related object of a notification."""
        # Create a post notification
        post = PostFactory(author=user)
        post_content_type = ContentType.objects.get_for_model(post)
        
        post_notification = NotificationFactory(
            recipient=user,
            sender=another_user,
            notification_type='post_like',
            content_type=post_content_type,
            object_id=post.id,
            text=f"{another_user.username} liked your post"
        )
        
        related_object = post_notification.get_related_object()
        assert related_object == post
        
        # Create a comment notification
        comment = CommentFactory(author=another_user, post=post)
        comment_content_type = ContentType.objects.get_for_model(comment)
        
        comment_notification = NotificationFactory(
            recipient=user,
            sender=another_user,
            notification_type='comment_like',
            content_type=comment_content_type,
            object_id=comment.id,
            text=f"{another_user.username} liked your comment"
        )
        
        related_object = comment_notification.get_related_object()
        assert related_object == comment

    @pytest.mark.unit
    @pytest.mark.model
    def test_unread_count_for_user(self, user, another_user):
        """Test getting the count of unread notifications for a user."""
        # Create some notifications
        NotificationFactory(recipient=user, sender=another_user, read=False)
        NotificationFactory(recipient=user, sender=another_user, read=False)
        NotificationFactory(recipient=user, sender=another_user, read=True)
        
        # Create a notification for another user
        NotificationFactory(recipient=another_user, sender=user, read=False)
        
        # Get the count of unread notifications for the user
        unread_count = Notification.objects.filter(recipient=user, read=False).count()
        
        assert unread_count == 2

    @pytest.mark.unit
    @pytest.mark.model
    def test_get_notifications_for_user(self, user, another_user):
        """Test getting notifications for a user."""
        # Create some notifications
        notification1 = NotificationFactory(recipient=user, sender=another_user)
        notification2 = NotificationFactory(recipient=user, sender=another_user)
        
        # Create a notification for another user
        NotificationFactory(recipient=another_user, sender=user)
        
        # Get notifications for the user
        notifications = Notification.objects.filter(recipient=user)
        
        assert notifications.count() == 2
        assert notification1 in notifications
        assert notification2 in notifications 