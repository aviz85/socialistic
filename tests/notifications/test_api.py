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
        # Create a notification for the authenticated user
        own_notification = NotificationFactory(
            recipient=user, 
            sender=another_user,
            type='post_like'
        )
        
        # Create a notification for another user
        other_notification = NotificationFactory(
            recipient=another_user,
            sender=user,
            type='post_like'
        )
        
        url = reverse('notification-list')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # If response has pagination
        notifications_data = response.data['results'] if 'results' in response.data else response.data
        
        # Check that only the user's notification is in the response
        notification_ids = [notif['id'] for notif in notifications_data]
        assert own_notification.id in notification_ids
        assert other_notification.id not in notification_ids


class TestNotificationMarkReadAPI:
    """Tests for marking notifications as read."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_notification_as_read(self, auth_client, user, notification):
        """Test marking a notification as read."""
        notification.is_read = False
        notification.save()
        
        url = reverse('notification-mark-read', kwargs={'pk': notification.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Reload the notification from the database
        notification.refresh_from_db()
        assert notification.is_read is True

    @pytest.mark.api
    @pytest.mark.integration
    def test_mark_notification_as_read_without_authentication(self, api_client, notification):
        """Test that an unauthenticated user cannot mark a notification as read."""
        url = reverse('notification-mark-read', kwargs={'pk': notification.id})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_mark_other_user_notification_as_read(self, auth_client, another_user):
        """Test that a user cannot mark another user's notification as read."""
        # Create a notification for another user
        notification = NotificationFactory(
            recipient=another_user,
            type='post_like',
            is_read=False
        )
        
        url = reverse('notification-mark-read', kwargs={'pk': notification.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify the notification is still unread
        notification.refresh_from_db()
        assert notification.is_read is False


class TestNotificationDeleteAPI:
    """Tests for deleting notifications."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_notification(self, auth_client, user, notification):
        """Test deleting a notification."""
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the notification was deleted
        assert not Notification.objects.filter(id=notification.id).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_notification_without_authentication(self, api_client, notification):
        """Test that an unauthenticated user cannot delete a notification."""
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_delete_other_user_notification(self, auth_client, another_user):
        """Test that a user cannot delete another user's notification."""
        # Create a notification for another user
        notification = NotificationFactory(
            recipient=another_user,
            type='post_like'
        )
        
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify the notification still exists
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
        # Create some unread notifications
        NotificationFactory(recipient=user, sender=another_user, is_read=False)
        NotificationFactory(recipient=user, sender=another_user, is_read=False)
        
        # Create a read notification
        NotificationFactory(recipient=user, sender=another_user, is_read=True)
        
        # Create an unread notification for another user
        NotificationFactory(recipient=another_user, sender=user, is_read=False)
        
        url = reverse('notification-unread-count')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2


class TestRealTimeNotificationAPI:
    """Tests for real-time notification API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_create_notification(self, auth_client, user, another_user):
        """Test creating a real-time notification."""
        post = PostFactory(author=user)
        content_type = ContentType.objects.get_for_model(post)
        
        url = reverse('notification-list')
        
        notification_data = {
            'recipient': another_user.id,
            'type': 'like',
            'content_type': content_type.id,
            'object_id': post.id,
            'text': f"{user.username} liked your post"
        }
        
        response = auth_client.post(url, notification_data)
        
        # Debug output
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify the notification was created
        notification = Notification.objects.get(id=response.data['id'])
        assert notification.recipient == another_user
        assert notification.sender == user
        assert notification.type == 'like'
        assert notification.text == f"{user.username} liked your post"
        assert notification.is_read is False 