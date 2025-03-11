import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from tests.factories import NotificationFactory, PostFactory

pytestmark = pytest.mark.django_db


class TestNotificationListAPI:
    """Tests for notification list API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_list_notifications(self, auth_client, user, another_user):
        """Test listing notifications for the authenticated user."""
        # Create some notifications for the authenticated user
        notification1 = NotificationFactory(recipient=user, sender=another_user)
        notification2 = NotificationFactory(recipient=user, sender=another_user)
        
        # Create a notification for another user
        NotificationFactory(recipient=another_user, sender=user)
        
        url = reverse('notification-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Assuming pagination is used
        
        # Check that both notifications are in the response
        notification_ids = [notification['id'] for notification in response.data['results']]
        assert notification1.id in notification_ids
        assert notification2.id in notification_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_notifications_without_authentication(self, api_client):
        """Test that an unauthenticated user cannot list notifications."""
        url = reverse('notification-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationReadAPI:
    """Tests for notification read API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_notification_as_read(self, auth_client, user, another_user):
        """Test marking a notification as read."""
        notification = NotificationFactory(recipient=user, sender=another_user, read=False)
        
        url = reverse('notification-read', kwargs={'pk': notification.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['read'] is True
        
        # Check that the notification was marked as read in the database
        notification.refresh_from_db()
        assert notification.read is True

    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_notification_as_unread(self, auth_client, user, another_user):
        """Test marking a notification as unread."""
        notification = NotificationFactory(recipient=user, sender=another_user, read=True)
        
        url = reverse('notification-unread', kwargs={'pk': notification.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['read'] is False
        
        # Check that the notification was marked as unread in the database
        notification.refresh_from_db()
        assert notification.read is False

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_mark_other_user_notification(self, auth_client, another_user):
        """Test that a user cannot mark another user's notification as read."""
        notification = NotificationFactory(recipient=another_user, read=False)
        
        url = reverse('notification-read', kwargs={'pk': notification.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the notification was not marked as read in the database
        notification.refresh_from_db()
        assert notification.read is False


class TestNotificationMarkAllReadAPI:
    """Tests for marking all notifications as read API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_all_notifications_as_read(self, auth_client, user, another_user):
        """Test marking all notifications as read."""
        # Create some unread notifications for the authenticated user
        notification1 = NotificationFactory(recipient=user, sender=another_user, read=False)
        notification2 = NotificationFactory(recipient=user, sender=another_user, read=False)
        
        # Create a notification for another user
        other_notification = NotificationFactory(recipient=another_user, sender=user, read=False)
        
        url = reverse('notification-mark-all-read')
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that all notifications for the authenticated user were marked as read
        notification1.refresh_from_db()
        notification2.refresh_from_db()
        other_notification.refresh_from_db()
        
        assert notification1.read is True
        assert notification2.read is True
        assert other_notification.read is False  # Other user's notification should not be affected


class TestNotificationDeleteAPI:
    """Tests for notification delete API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_notification(self, auth_client, user, another_user):
        """Test deleting a notification."""
        notification = NotificationFactory(recipient=user, sender=another_user)
        
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the notification was deleted from the database
        assert not Notification.objects.filter(id=notification.id).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_delete_other_user_notification(self, auth_client, another_user):
        """Test that a user cannot delete another user's notification."""
        notification = NotificationFactory(recipient=another_user)
        
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the notification was not deleted from the database
        assert Notification.objects.filter(id=notification.id).exists()


class TestNotificationCountAPI:
    """Tests for notification count API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_get_unread_notification_count(self, auth_client, user, another_user):
        """Test getting the count of unread notifications."""
        # Create some unread notifications for the authenticated user
        NotificationFactory(recipient=user, sender=another_user, read=False)
        NotificationFactory(recipient=user, sender=another_user, read=False)
        
        # Create a read notification for the authenticated user
        NotificationFactory(recipient=user, sender=another_user, read=True)
        
        # Create an unread notification for another user
        NotificationFactory(recipient=another_user, sender=user, read=False)
        
        url = reverse('notification-unread-count')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2


class TestRealTimeNotificationAPI:
    """Tests for real-time notification API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_create_notification(self, auth_client, user, another_user):
        """Test creating a notification."""
        # This would typically be done by a signal handler or a background task,
        # but we'll test the API endpoint that would be called by the frontend
        post = PostFactory(author=user)
        content_type = ContentType.objects.get_for_model(post)
        
        url = reverse('notification-create')
        data = {
            'recipient': user.id,
            'sender': another_user.id,
            'notification_type': 'post_like',
            'content_type': content_type.id,
            'object_id': post.id,
            'text': f"{another_user.username} liked your post"
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['recipient'] == user.id
        assert response.data['sender'] == another_user.id
        assert response.data['notification_type'] == 'post_like'
        assert response.data['text'] == f"{another_user.username} liked your post"
        assert response.data['read'] is False
        
        # Check that the notification was created in the database
        assert Notification.objects.filter(
            recipient=user,
            sender=another_user,
            notification_type='post_like',
            content_type=content_type,
            object_id=post.id
        ).exists() 