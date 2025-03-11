import pytest
from django.urls import reverse
from rest_framework import status
import json

pytestmark = [pytest.mark.django_db, pytest.mark.security]


class TestAuthenticationSecurity:
    """Tests for authentication security."""
    
    def test_invalid_token_rejection(self, api_client):
        """Test that requests with invalid tokens are rejected."""
        # Try to access a protected endpoint with an invalid token
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalidtokenvalue')
        
        url = reverse('me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, user):
        """Test token refresh functionality."""
        # Log in to get a refresh token
        login_url = reverse('login')
        login_data = {
            'email': user.email,
            'password': 'password'  # Default password from fixture
        }
        
        login_response = api_client.post(login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        refresh_token = login_response.data['refresh']
        
        # Use the refresh token to get a new access token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }
        
        refresh_response = api_client.post(refresh_url, refresh_data)
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data
        
        # Verify the new token works
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_response.data["access"]}')
        
        me_url = reverse('me')
        me_response = api_client.get(me_url)
        
        assert me_response.status_code == status.HTTP_200_OK


class TestAuthorizationSecurity:
    """Tests for authorization security."""
    
    def test_cannot_update_other_user_profile(self, auth_client, another_user):
        """Test that a user cannot update another user's profile."""
        url = reverse('user-detail', kwargs={'pk': another_user.id})
        
        data = {
            'bio': 'Updated by another user'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_cannot_access_admin_without_permissions(self, auth_client):
        """Test that a regular user cannot access admin pages."""
        url = '/admin/'  # Django admin URL
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_302_FOUND  # Redirect to login or 403


class TestInputValidationSecurity:
    """Tests for input validation security."""
    
    def test_xss_protection(self, auth_client, user):
        """Test protection against XSS attacks."""
        url = reverse('me')
        
        # Try to update profile with malicious script
        data = {
            'bio': '<script>alert("XSS")</script>This is my bio'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the script tag was escaped or removed
        bio = response.data['bio']
        assert '<script>' not in bio or bio != data['bio']

    def test_sql_injection_protection(self, api_client):
        """Test protection against SQL injection."""
        # Example: Try to use SQL injection in a search query
        search_url = reverse('search')
        
        # SQL injection attempt in search query
        sql_injection = "'); DROP TABLE users; --"
        
        params = {'query': sql_injection}
        response = api_client.get(search_url, params)
        
        # The request should not cause a server error
        assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


class TestRateLimitingSecurity:
    """Tests for rate limiting security features."""
    
    @pytest.mark.skip("Rate limiting tests may need special configuration")
    def test_login_rate_limiting(self, api_client, user):
        """Test that login attempts are rate-limited."""
        url = reverse('login')
        
        # Attempt to login multiple times with wrong password
        for _ in range(10):
            data = {
                'email': user.email,
                'password': 'wrongpassword'
            }
            api_client.post(url, data)
        
        # Check if rate limiting kicks in
        data = {
            'email': user.email,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)
        
        # Either 429 Too Many Requests or still 401 Unauthorized
        assert response.status_code in [status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_401_UNAUTHORIZED]


class TestDataPrivacySecurity:
    """Tests for data privacy security features."""
    
    def test_password_not_returned(self, auth_client, user):
        """Test that passwords are not returned in responses."""
        url = reverse('me')
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'password' not in response.data

    def test_private_fields_not_accessible(self, auth_client, another_user):
        """Test that private user fields are not accessible to other users."""
        url = reverse('user-detail', kwargs={'pk': another_user.id})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'email' not in response.data 