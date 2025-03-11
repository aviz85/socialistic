import pytest
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from users.models import User, Skill, ProgrammingLanguage, Follow
from tests.factories import UserFactory, SkillFactory, ProgrammingLanguageFactory, FollowFactory

pytestmark = pytest.mark.django_db


class TestUserModel:
    """Unit tests for the User model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_user_creation(self):
        """Test creating a user."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            full_name='Test User'
        )
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.full_name == 'Test User'
        assert user.check_password('testpassword')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    @pytest.mark.unit
    @pytest.mark.model
    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpassword'
        )
        assert admin.is_active
        assert admin.is_staff
        assert admin.is_superuser

    @pytest.mark.unit
    @pytest.mark.model
    def test_email_unique(self):
        """Test that email addresses are unique."""
        User.objects.create_user(
            email='duplicate@example.com',
            username='user1',
            password='password'
        )
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                User.objects.create_user(
                    email='duplicate@example.com',
                    username='user2',
                    password='password'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_username_unique(self):
        """Test that usernames are unique."""
        User.objects.create_user(
            email='user1@example.com',
            username='duplicate',
            password='password'
        )
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                User.objects.create_user(
                    email='user2@example.com',
                    username='duplicate',
                    password='password'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_email_required(self):
        """Test that email is required."""
        with pytest.raises(ValueError):
            User.objects.create_user(
                email='',
                username='testuser',
                password='password'
            )

    @pytest.mark.unit
    @pytest.mark.model
    def test_username_required(self):
        """Test that username is required."""
        with pytest.raises(ValueError):
            User.objects.create_user(
                email='test@example.com',
                username='',
                password='password'
            )

    @pytest.mark.unit
    @pytest.mark.model
    def test_user_str(self):
        """Test the string representation of a user."""
        user = UserFactory(username='testuser')
        assert str(user) == 'testuser'

    @pytest.mark.unit
    @pytest.mark.model
    def test_follow_relationship(self, user, another_user):
        """Test follow relationship between users."""
        # User follows another_user
        user.follow(another_user)
        
        # Check that the follow relationship exists
        assert user.following.filter(following=another_user).exists()
        assert another_user.followers.filter(follower=user).exists()
        
        # Check follower/following counts
        assert user.following_count == 1
        assert another_user.followers_count == 1
        
        # User unfollows another_user
        user.unfollow(another_user)
        
        # Check that the follow relationship no longer exists
        assert not user.following.filter(following=another_user).exists()
        assert not another_user.followers.filter(follower=user).exists()

    @pytest.mark.unit
    @pytest.mark.model
    def test_cannot_follow_self(self, user):
        """Test that a user cannot follow themselves."""
        user.follow(user)
        assert not user.following.filter(following=user).exists()


class TestSkillModel:
    """Unit tests for the Skill model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_skill_creation(self):
        """Test creating a skill."""
        skill = Skill.objects.create(name='Python', category='backend')
        assert skill.name == 'Python'
        assert skill.category == 'backend'
        assert str(skill) == 'Python'

    @pytest.mark.unit
    @pytest.mark.model
    def test_skill_unique_name(self):
        """Test that skill names are unique."""
        Skill.objects.create(name='JavaScript', category='frontend')
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                Skill.objects.create(name='JavaScript', category='backend')

    @pytest.mark.unit
    @pytest.mark.model
    def test_skill_user_relationship(self, user):
        """Test the many-to-many relationship between skills and users."""
        skill1 = SkillFactory(name='Skill1')
        skill2 = SkillFactory(name='Skill2')
        
        # Add skills to user
        user.skills.add(skill1, skill2)
        
        # Check that user has skills
        assert user.skills.count() == 2
        assert skill1 in user.skills.all()
        assert skill2 in user.skills.all()
        
        # Check that skills have user
        assert user in skill1.users.all()
        assert user in skill2.users.all()


class TestProgrammingLanguageModel:
    """Unit tests for the ProgrammingLanguage model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_language_creation(self):
        """Test creating a programming language."""
        language = ProgrammingLanguage.objects.create(name='Ruby')
        assert language.name == 'Ruby'
        assert str(language) == 'Ruby'

    @pytest.mark.unit
    @pytest.mark.model
    def test_language_unique_name(self):
        """Test that language names are unique."""
        ProgrammingLanguage.objects.create(name='Go')
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                ProgrammingLanguage.objects.create(name='Go')


class TestFollowModel:
    """Unit tests for the Follow model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_follow_creation(self, user, another_user):
        """Test creating a follow relationship."""
        follow = Follow.objects.create(follower=user, following=another_user)
        assert follow.follower == user
        assert follow.following == another_user
        assert str(follow) == f"{user.username} follows {another_user.username}"

    @pytest.mark.unit
    @pytest.mark.model
    def test_follow_unique_constraint(self, user, another_user):
        """Test that a user can only follow another user once."""
        Follow.objects.create(follower=user, following=another_user)
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                Follow.objects.create(follower=user, following=another_user) 