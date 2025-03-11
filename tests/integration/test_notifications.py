import pytest
from django.urls import reverse
from rest_framework import status
from notifications.models import Notification

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


class TestFollowNotification:
    """Test notifications for follow actions."""
    
    def test_follow_creates_notification(self, auth_client, user, another_user):
        """Test that following a user creates a notification."""
        # Follow another user
        url = reverse('user-follow', kwargs={'pk': another_user.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created
        assert Notification.objects.filter(
            recipient=another_user,
            sender=user,
            notification_type='follow'
        ).exists()


class TestCommentNotification:
    """Test notifications for comment actions."""
    
    def test_comment_creates_notification(self, auth_client, user, post):
        """Test that commenting on a post creates a notification."""
        # Comment on a post
        url = reverse('post-comments', kwargs={'pk': post.id})
        data = {
            'content': 'Test comment'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created for the post author
        assert Notification.objects.filter(
            recipient=post.author,
            sender=user,
            notification_type='comment'
        ).exists()


class TestLikeNotification:
    """Test notifications for like actions."""
    
    def test_post_like_creates_notification(self, auth_client, user, post):
        """Test that liking a post creates a notification."""
        # Like a post
        url = reverse('post-like', kwargs={'pk': post.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created for the post author
        assert Notification.objects.filter(
            recipient=post.author,
            sender=user,
            notification_type='post_like'
        ).exists()

    @pytest.mark.skip("Comment like endpoint not implemented yet")
    def test_comment_like_creates_notification(self, auth_client, user, comment):
        """Test that liking a comment creates a notification."""
        # Like a comment
        url = reverse('comment-like', kwargs={'comment_id': comment.id})
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created for the comment author
        assert Notification.objects.filter(
            recipient=comment.author,
            sender=user,
            notification_type='comment_like'
        ).exists()


class TestProjectNotification:
    """Test notifications for project actions."""
    
    def test_collaboration_request_creates_notification(self, auth_client, user, another_user):
        """Test that requesting to collaborate on a project creates a notification."""
        # Create a project
        from projects.models import Project
        project = Project.objects.create(
            creator=another_user,
            title='Test Project',
            description='Test project description'
        )
        
        # Request to collaborate
        url = reverse('project-collaborate', kwargs={'pk': project.id})
        data = {
            'message': 'I would like to collaborate on this project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that a notification was created for the project creator
        assert Notification.objects.filter(
            recipient=another_user,
            sender=user,
            notification_type='collaboration_request'
        ).exists()

    def test_collaboration_accepted_creates_notification(self, auth_client, user, another_user):
        """Test that accepting a collaboration request creates a notification."""
        # Create a project
        from projects.models import Project, CollaborationRequest
        project = Project.objects.create(
            creator=user,
            title='Test Project',
            description='Test project description'
        )
        
        # Create a collaboration request
        request = CollaborationRequest.objects.create(
            user=another_user,
            project=project,
            message='I would like to collaborate on this project.'
        )
        
        # Accept the request
        url = reverse('collaboration-request-respond', kwargs={'pk': request.id})
        data = {
            'status': 'accepted'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that a notification was created for the requester
        assert Notification.objects.filter(
            recipient=another_user,
            sender=user,
            notification_type='collaboration_accepted'
        ).exists() 