import pytest
from django.urls import reverse
from rest_framework import status
from users.models import User, Follow
from tests.factories import UserFactory, SkillFactory, ProgrammingLanguageFactory

pytestmark = pytest.mark.django_db


class TestUserRegistrationAPI:
    """Tests for user registration API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_user_registration(self, api_client):
        """Test that a user can register via the API."""
        url = reverse('user-register')
        
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123',
            'full_name': 'New User'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        
        # Check that the user was created in the database
        user = User.objects.get(email='newuser@example.com')
        assert user.username == 'newuser'
        assert user.full_name == 'New User'
        assert user.check_password('securepassword123')

    @pytest.mark.api
    @pytest.mark.integration
    def test_register_with_existing_email(self, api_client, user):
        """Test that registration fails with an existing email."""
        url = reverse('user-register')
        
        data = {
            'email': user.email,  # Using existing email
            'username': 'newusername',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123',
            'full_name': 'Another User'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    @pytest.mark.api
    @pytest.mark.integration
    def test_register_with_existing_username(self, api_client, user):
        """Test that registration fails with an existing username."""
        url = reverse('user-register')
        
        data = {
            'email': 'unique@example.com',
            'username': user.username,  # Using existing username
            'password': 'securepassword123',
            'password_confirm': 'securepassword123',
            'full_name': 'Another User'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    @pytest.mark.api
    @pytest.mark.integration
    def test_register_password_mismatch(self, api_client):
        """Test that registration fails when passwords don't match."""
        url = reverse('user-register')
        
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepassword123',
            'password_confirm': 'differentpassword123',  # Different password
            'full_name': 'New User'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data or 'password_confirm' in response.data


class TestUserLoginAPI:
    """Tests for user login API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_user_login(self, api_client, user):
        """Test that a user can login via the API."""
        url = reverse('user-login')
        
        data = {
            'email': user.email,
            'password': 'password'  # Default password from the fixture
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert response.data['user']['email'] == user.email
        assert response.data['user']['username'] == user.username

    @pytest.mark.api
    @pytest.mark.integration
    def test_login_with_invalid_credentials(self, api_client, user):
        """Test that login fails with invalid credentials."""
        url = reverse('user-login')
        
        data = {
            'email': user.email,
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data


class TestUserProfileAPI:
    """Tests for user profile API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_get_own_profile(self, auth_client, user):
        """Test that a user can get their own profile."""
        url = reverse('user-profile')
        
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['username'] == user.username
        assert response.data['full_name'] == user.full_name

    @pytest.mark.api
    @pytest.mark.integration
    def test_update_profile(self, auth_client, user):
        """Test that a user can update their profile."""
        url = reverse('user-profile')
        
        data = {
            'full_name': 'Updated Name',
            'bio': 'Updated bio information'
        }
        
        response = auth_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Updated Name'
        assert response.data['bio'] == 'Updated bio information'
        
        # Check that the user was updated in the database
        user.refresh_from_db()
        assert user.full_name == 'Updated Name'
        assert user.bio == 'Updated bio information'

    @pytest.mark.api
    @pytest.mark.integration
    def test_update_profile_not_authenticated(self, api_client):
        """Test that an unauthenticated user cannot update a profile."""
        url = reverse('user-profile')
        
        data = {
            'full_name': 'Updated Name',
            'bio': 'Updated bio information'
        }
        
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_view_other_user_profile(self, auth_client, another_user):
        """Test that a user can view another user's profile."""
        url = reverse('user-detail', kwargs={'username': another_user.username})
        
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == another_user.username
        assert response.data['full_name'] == another_user.full_name
        # Check that sensitive fields are not included
        assert 'email' not in response.data


class TestUserSkillsAPI:
    """Tests for user skills API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_add_skill_to_profile(self, auth_client, user):
        """Test that a user can add skills to their profile."""
        url = reverse('user-skills')
        
        # Create skills to add
        skill1 = SkillFactory(name='Django')
        skill2 = SkillFactory(name='React')
        
        data = {
            'skill_ids': [skill1.id, skill2.id]
        }
        
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the skills were added in the database
        user.refresh_from_db()
        assert user.skills.count() == 2
        assert skill1 in user.skills.all()
        assert skill2 in user.skills.all()

    @pytest.mark.api
    @pytest.mark.integration
    def test_remove_skill_from_profile(self, auth_client, user):
        """Test that a user can remove skills from their profile."""
        # Add skills to user
        skill1 = SkillFactory(name='Django')
        skill2 = SkillFactory(name='React')
        user.skills.add(skill1, skill2)
        
        url = reverse('user-remove-skill', kwargs={'skill_id': skill1.id})
        
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the skill was removed in the database
        user.refresh_from_db()
        assert user.skills.count() == 1
        assert skill1 not in user.skills.all()
        assert skill2 in user.skills.all()


class TestFollowAPI:
    """Tests for follow API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_follow_user(self, auth_client, user, another_user):
        """Test that a user can follow another user."""
        url = reverse('user-follow', kwargs={'username': another_user.username})
        
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that the follow relationship was created in the database
        assert Follow.objects.filter(follower=user, following=another_user).exists()
        
        # Check follower/following counts
        user.refresh_from_db()
        another_user.refresh_from_db()
        assert user.following_count == 1
        assert another_user.followers_count == 1

    @pytest.mark.api
    @pytest.mark.integration
    def test_unfollow_user(self, auth_client, user, another_user):
        """Test that a user can unfollow another user."""
        # Create follow relationship
        Follow.objects.create(follower=user, following=another_user)
        
        url = reverse('user-unfollow', kwargs={'username': another_user.username})
        
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the follow relationship was removed from the database
        assert not Follow.objects.filter(follower=user, following=another_user).exists()
        
        # Check follower/following counts
        user.refresh_from_db()
        another_user.refresh_from_db()
        assert user.following_count == 0
        assert another_user.followers_count == 0

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_follow_self(self, auth_client, user):
        """Test that a user cannot follow themselves."""
        url = reverse('user-follow', kwargs={'username': user.username})
        
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that no follow relationship was created
        assert not Follow.objects.filter(follower=user, following=user).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_followers(self, auth_client, user, another_user):
        """Test that a user can list their followers."""
        # Create follow relationship
        Follow.objects.create(follower=another_user, following=user)
        
        url = reverse('user-followers')
        
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['username'] == another_user.username

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_following(self, auth_client, user, another_user):
        """Test that a user can list the users they are following."""
        # Create follow relationship
        Follow.objects.create(follower=user, following=another_user)
        
        url = reverse('user-following')
        
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['username'] == another_user.username 