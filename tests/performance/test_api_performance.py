import pytest
import time
from django.urls import reverse
from rest_framework import status
from tests.factories import PostFactory, UserFactory

pytestmark = [pytest.mark.django_db, pytest.mark.performance]


class TestAPIPerformance:
    """Performance tests for API endpoints."""

    def test_post_list_performance(self, auth_client, user):
        """Test the performance of the post list endpoint."""
        # Create a large number of posts
        num_posts = 50
        for _ in range(num_posts):
            PostFactory(author=user)
        
        # Measure the time it takes to retrieve the posts
        url = reverse('post-list')
        start_time = time.time()
        response = auth_client.get(url)
        end_time = time.time()
        
        # Check that the response is successful
        assert response.status_code == status.HTTP_200_OK
        
        # Calculate the response time
        response_time = end_time - start_time
        
        # Assert that the response time is within an acceptable range
        # This threshold might need to be adjusted based on the actual performance
        assert response_time < 1.0, f"Response time was {response_time} seconds"

    def test_user_search_performance(self, auth_client):
        """Test the performance of the user search endpoint."""
        # Create a large number of users
        num_users = 50
        for i in range(num_users):
            UserFactory(username=f"testuser{i}", email=f"testuser{i}@example.com")
        
        # Measure the time it takes to search for users
        url = reverse('user-search') + "?query=testuser"
        start_time = time.time()
        response = auth_client.get(url)
        end_time = time.time()
        
        # Check that the response is successful
        assert response.status_code == status.HTTP_200_OK
        
        # Calculate the response time
        response_time = end_time - start_time
        
        # Assert that the response time is within an acceptable range
        assert response_time < 1.0, f"Response time was {response_time} seconds"

    def test_post_creation_performance(self, auth_client, user):
        """Test the performance of creating a post."""
        url = reverse('post-list')
        data = {
            'content': 'Test post content',
            'code_snippet': 'print("Hello, world!")'
        }
        
        # Measure the time it takes to create a post
        start_time = time.time()
        response = auth_client.post(url, data)
        end_time = time.time()
        
        # Check that the response is successful
        assert response.status_code == status.HTTP_201_CREATED
        
        # Calculate the response time
        response_time = end_time - start_time
        
        # Assert that the response time is within an acceptable range
        assert response_time < 1.0, f"Response time was {response_time} seconds"

    def test_notification_list_performance(self, auth_client, user, another_user):
        """Test the performance of the notification list endpoint."""
        # Create a large number of notifications
        num_notifications = 50
        from tests.factories import NotificationFactory
        for _ in range(num_notifications):
            NotificationFactory(recipient=user, sender=another_user)
        
        # Measure the time it takes to retrieve the notifications
        url = reverse('notification-list')
        start_time = time.time()
        response = auth_client.get(url)
        end_time = time.time()
        
        # Check that the response is successful
        assert response.status_code == status.HTTP_200_OK
        
        # Calculate the response time
        response_time = end_time - start_time
        
        # Assert that the response time is within an acceptable range
        assert response_time < 1.0, f"Response time was {response_time} seconds"

    def test_project_list_performance(self, auth_client, user):
        """Test the performance of the project list endpoint."""
        # Create a large number of projects
        num_projects = 50
        from tests.factories import ProjectFactory
        for _ in range(num_projects):
            ProjectFactory(creator=user)
        
        # Measure the time it takes to retrieve the projects
        url = reverse('project-list')
        start_time = time.time()
        response = auth_client.get(url)
        end_time = time.time()
        
        # Check that the response is successful
        assert response.status_code == status.HTTP_200_OK
        
        # Calculate the response time
        response_time = end_time - start_time
        
        # Assert that the response time is within an acceptable range
        assert response_time < 1.0, f"Response time was {response_time} seconds" 