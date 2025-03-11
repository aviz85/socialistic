import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import PostFactory, CommentFactory, ProjectFactory

pytestmark = [pytest.mark.django_db, pytest.mark.security]


class TestAuthorizationSecurity:
    """Security tests for authorization."""

    def test_unauthenticated_access_to_protected_endpoints(self, api_client):
        """Test that unauthenticated users cannot access protected endpoints."""
        # List of protected endpoints to test
        protected_endpoints = [
            reverse('user-profile'),
            reverse('user-followers'),
            reverse('user-following'),
            reverse('post-list'),  # POST method requires authentication
            reverse('notification-list'),
            reverse('project-list'),  # POST method requires authentication
        ]
        
        # Try to access each endpoint without authentication
        for endpoint in protected_endpoints:
            response = api_client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            
            # For endpoints that support POST
            if endpoint in [reverse('post-list'), reverse('project-list')]:
                response = api_client.post(endpoint, {})
                assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_post_modification(self, auth_client, user, another_user):
        """Test that users cannot modify posts they don't own."""
        # Create a post by another user
        post = PostFactory(author=another_user)
        
        # Try to update the post
        url = reverse('post-detail', kwargs={'pk': post.id})
        data = {
            'content': 'Updated content'
        }
        response = auth_client.patch(url, data)
        
        # This should fail with a 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to delete the post
        response = auth_client.delete(url)
        
        # This should also fail with a 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_comment_modification(self, auth_client, user, another_user):
        """Test that users cannot modify comments they don't own."""
        # Create a post and a comment by another user
        post = PostFactory(author=user)
        comment = CommentFactory(author=another_user, post=post)
        
        # Try to update the comment
        url = reverse('comment-detail', kwargs={'pk': comment.id})
        data = {
            'content': 'Updated comment'
        }
        response = auth_client.patch(url, data)
        
        # This should fail with a 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to delete the comment
        response = auth_client.delete(url)
        
        # This should also fail with a 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_project_modification(self, auth_client, user, another_user):
        """Test that users cannot modify projects they don't own."""
        # Create a project by another user
        project = ProjectFactory(creator=another_user)
        
        # Try to update the project
        url = reverse('project-detail', kwargs={'pk': project.id})
        data = {
            'title': 'Updated Project Title'
        }
        response = auth_client.patch(url, data)
        
        # This should fail with a 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to delete the project
        response = auth_client.delete(url)
        
        # This should also fail with a 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_notification_access(self, auth_client, user, another_user):
        """Test that users cannot access notifications that don't belong to them."""
        # Create a notification for another user
        from tests.factories import NotificationFactory
        notification = NotificationFactory(recipient=another_user, sender=user)
        
        # Try to access the notification
        url = reverse('notification-detail', kwargs={'pk': notification.id})
        response = auth_client.get(url)
        
        # This should fail with a 404 Not Found (or 403 Forbidden, depending on implementation)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]
        
        # Try to mark the notification as read
        url = reverse('notification-read', kwargs={'pk': notification.id})
        response = auth_client.post(url)
        
        # This should also fail
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_admin_access_protection(self, api_client):
        """Test that the admin interface is protected."""
        # Try to access the admin interface without authentication
        url = reverse('admin:index')
        response = api_client.get(url)
        
        # This should redirect to the login page
        assert response.status_code == status.HTTP_302_FOUND
        assert 'login' in response.url

    def test_api_token_validation(self, api_client):
        """Test that invalid API tokens are rejected."""
        # Try to access a protected endpoint with an invalid token
        api_client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        
        url = reverse('user-profile')
        response = api_client.get(url)
        
        # This should fail with a 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 