import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from posts.models import Post, PostLike, Comment, CommentLike
from users.models import Follow
from tests.factories import UserFactory, PostFactory, CommentFactory

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


class TestNotificationFlow:
    """Integration tests for the notification flow."""

    def test_post_like_notification(self, auth_client, user, another_user):
        """Test that a notification is created when a user likes a post."""
        # Create a post
        post = PostFactory(author=another_user)
        
        # Like the post
        url = reverse('post-like', kwargs={'pk': post.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created
        content_type = ContentType.objects.get_for_model(Post)
        notification = Notification.objects.filter(
            recipient=another_user,
            sender=user,
            type='like',
            content_type=content_type,
            object_id=post.id
        ).first()
        
        assert notification is not None
        assert notification.text == f"{user.username} liked your post"
        assert notification.is_read is False

    def test_comment_notification(self, auth_client, user, another_user):
        """Test that a notification is created when a user comments on a post."""
        # Create a post
        post = PostFactory(author=another_user)
        
        # Comment on the post
        url = reverse('post-comments', kwargs={'pk': post.id})
        data = {
            'content': 'Test comment'
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created
        content_type = ContentType.objects.get_for_model(Comment)
        comment_id = response.data['id']
        notification = Notification.objects.filter(
            recipient=another_user,
            sender=user,
            type='comment',
            content_type=content_type,
            object_id=comment_id
        ).first()
        
        assert notification is not None
        assert notification.text == f"{user.username} commented on your post"
        assert notification.is_read is False

    def test_comment_like_notification(self, auth_client, user, another_user):
        """Test that a notification is created when a user likes a comment."""
        # Create a post and comment
        post = PostFactory(author=user)
        comment = CommentFactory(author=another_user, post=post)
        
        # Like the comment
        url = reverse('comment-like', kwargs={'pk': comment.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created
        content_type = ContentType.objects.get_for_model(Comment)
        notification = Notification.objects.filter(
            recipient=another_user,
            sender=user,
            type='like',
            content_type=content_type,
            object_id=comment.id
        ).first()
        
        assert notification is not None
        assert notification.text == f"{user.username} liked your comment"
        assert notification.is_read is False

    def test_follow_notification(self, auth_client, user, another_user):
        """Test that a notification is created when a user follows another user."""
        # Follow the user
        url = reverse('user-follow', kwargs={'pk': another_user.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created
        from django.contrib.auth import get_user_model
        User = get_user_model()
        content_type = ContentType.objects.get_for_model(User)
        notification = Notification.objects.filter(
            recipient=another_user,
            sender=user,
            type='follow',
            content_type=content_type,
            object_id=another_user.id
        ).first()
        
        assert notification is not None
        assert notification.text == f"{user.username} started following you"
        assert notification.is_read is False

    def test_collaboration_request_notification(self, auth_client, user, another_user):
        """Test that a notification is created when a user requests to collaborate on a project."""
        # Create a project
        url = reverse('project-list')
        project_data = {
            'title': 'Test Project',
            'description': 'A test project'
        }
        project_response = auth_client.post(url, project_data)
        assert project_response.status_code == status.HTTP_201_CREATED
        project_id = project_response.data['id']
        
        # Switch to another user
        auth_client.force_authenticate(user=another_user)
        
        # Request to collaborate
        url = reverse('project-collaborate', kwargs={'pk': project_id})
        data = {
            'message': 'I would like to collaborate on this project.'
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created
        from projects.models import CollaborationRequest
        content_type = ContentType.objects.get_for_model(CollaborationRequest)
        request_id = response.data['id']
        notification = Notification.objects.filter(
            recipient=user,
            sender=another_user,
            type='project_request',
            content_type=content_type,
            object_id=request_id
        ).first()
        
        assert notification is not None
        assert notification.text == f"{another_user.username} requested to collaborate on Test Project"
        assert notification.is_read is False

    def test_mark_notification_as_read(self, auth_client, user, another_user):
        """Test marking a notification as read and checking the unread count."""
        # Create some notifications
        from tests.factories import NotificationFactory
        notification1 = NotificationFactory(recipient=user, sender=another_user, is_read=False)
        notification2 = NotificationFactory(recipient=user, sender=another_user, is_read=False)
        
        # Check the unread count
        url = reverse('notification-unread-count')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Mark one notification as read
        url = reverse('notification-mark-read', kwargs={'pk': notification1.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check the unread count again
        url = reverse('notification-unread-count')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        
        # Mark all notifications as read
        url = reverse('notification-mark-all-read')
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check the unread count again
        url = reverse('notification-unread-count')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0 