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
    def test_list_notifications(self, auth_client, user, notification):
        """Test listing notifications for a user."""
        url = reverse('notification-list')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1 or len(response.data['results']) == 1  # Handle pagination
        
        # If response has pagination
        notifications_data = response.data['results'] if 'results' in response.data else response.data
        
        # Check that notification is in the response
        notification_ids = [notif['id'] for notif in notifications_data]
        assert notification.id in notification_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_notifications_without_authentication(self, api_client):
        """Test that an unauthenticated user cannot list notifications."""
        url = reverse('notification-list')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_notifications_only_shows_own_notifications(self, auth_client, user, another_user):
        """Test that a user can only see their own notifications."""
        # Create a notification for current user
        notification_for_user = Notification.objects.create(
            recipient=user,
            sender=another_user,
            notification_type='follow',
            text=f"{another_user.username} started following you."
        )
        
        # Create a notification for another user
        notification_for_another = Notification.objects.create(
            recipient=another_user,
            sender=user,
            notification_type='follow',
            text=f"{user.username} started following you."
        )
        
        url = reverse('notification-list')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify only user's own notifications are returned, handling potential pagination
        notifications_data = response.data['results'] if 'results' in response.data else response.data
        notification_ids = [notif['id'] for notif in notifications_data]
        
        assert notification_for_user.id in notification_ids
        assert notification_for_another.id not in notification_ids


class TestNotificationMarkReadAPI:
    """Tests for marking notifications as read."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_notification_as_read(self, auth_client, user, notification):
        """Test marking a notification as read."""
        # Ensure notification is unread
        notification.is_read = False
        notification.save()
        
        url = reverse('notification-read', kwargs={'pk': notification.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_read'] == True
        
        # Check that the notification was marked as read in the database
        notification.refresh_from_db()
        assert notification.is_read == True

    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_notification_as_read_without_authentication(self, api_client, notification):
        """Test that an unauthenticated user cannot mark a notification as read."""
        url = reverse('notification-read', kwargs={'pk': notification.id})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_mark_other_user_notification_as_read(self, auth_client, another_user):
        """Test that a user cannot mark another user's notification as read."""
        # Create a notification for another user
        notification = Notification.objects.create(
            recipient=another_user,
            sender=auth_client.handler._force_user,  # The authenticated user
            notification_type='follow',
            text=f"{auth_client.handler._force_user.username} started following you."
        )
        
        url = reverse('notification-read', kwargs={'pk': notification.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the notification was not marked as read in the database
        notification.refresh_from_db()
        assert notification.is_read == False


class TestNotificationDeleteAPI:
    """Tests for deleting notifications."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_notification(self, auth_client, user, notification):
        """Test deleting a notification."""
        url = reverse('notification-delete', kwargs={'pk': notification.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the notification was deleted from the database
        assert not Notification.objects.filter(id=notification.id).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_notification_without_authentication(self, api_client, notification):
        """Test that an unauthenticated user cannot delete a notification."""
        url = reverse('notification-delete', kwargs={'pk': notification.id})
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_delete_other_user_notification(self, auth_client, another_user):
        """Test that a user cannot delete another user's notification."""
        # Create a notification for another user
        notification = Notification.objects.create(
            recipient=another_user,
            sender=auth_client.handler._force_user,  # The authenticated user
            notification_type='follow',
            text=f"{auth_client.handler._force_user.username} started following you."
        )
        
        url = reverse('notification-delete', kwargs={'pk': notification.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the notification was not deleted from the database
        assert Notification.objects.filter(id=notification.id).exists()


class TestNotificationSettingAPI:
    """Tests for notification settings."""
    
    @pytest.mark.skip("Notification settings endpoint needs to be checked")
    @pytest.mark.api
    @pytest.mark.integration
    def test_update_notification_settings(self, auth_client, user):
        """Test updating notification settings."""
        url = reverse('notification-settings')
        
        data = {
            'email_notifications': False,
            'browser_notifications': True
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email_notifications'] == False
        assert response.data['browser_notifications'] == True
        
        # Check that the settings were updated in the database
        user.refresh_from_db()
        assert user.notification_settings.email_notifications == False
        assert user.notification_settings.browser_notifications == True

    @pytest.mark.skip("Notification settings endpoint needs to be checked")
    @pytest.mark.api
    @pytest.mark.integration
    def test_update_notification_settings_without_authentication(self, api_client):
        """Test that an unauthenticated user cannot update notification settings."""
        url = reverse('notification-settings')
        
        data = {
            'email_notifications': False,
            'browser_notifications': True
        }
        
        response = api_client.patch(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


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