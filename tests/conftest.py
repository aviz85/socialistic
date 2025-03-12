import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType
from users.models import Skill, ProgrammingLanguage, Follow
from posts.models import Post, Comment, PostLike, CommentLike
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from notifications.models import Notification
from rest_framework_simplejwt.tokens import RefreshToken
import datetime

User = get_user_model()


@pytest.fixture
def api_client():
    """Returns an authenticated API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Creates a user for testing."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password',
        full_name='Test User',
        bio='Test user bio'
    )
    return user


@pytest.fixture
def auth_client(api_client, user):
    """Returns an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_user(db):
    """Creates an admin user for testing."""
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword',
        full_name='Admin User'
    )
    return admin


@pytest.fixture
def another_user(db):
    """Creates another user for testing."""
    user = User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='password',
        full_name='Another User',
        bio='Another test user bio'
    )
    return user


@pytest.fixture
def programming_language(db):
    """Creates a programming language for testing."""
    language = ProgrammingLanguage.objects.create(name='Python')
    return language


@pytest.fixture
def skill(db):
    """Creates a skill for testing."""
    skill = Skill.objects.create(name='Django', category='backend')
    return skill


@pytest.fixture
def skills_set(db):
    """Creates a set of skills for testing."""
    skills = [
        Skill.objects.create(name='React', category='frontend'),
        Skill.objects.create(name='Node.js', category='backend'),
        Skill.objects.create(name='PostgreSQL', category='database')
    ]
    return skills


@pytest.fixture
def follow_relationship(db, user, another_user):
    """Creates a follow relationship between two users."""
    follow = Follow.objects.create(follower=user, following=another_user)
    return follow


@pytest.fixture
def post(db, user, programming_language):
    """Creates a post for testing."""
    post = Post.objects.create(
        author=user,
        content='Test post content',
        code_snippet='print("Hello, world!")',
        programming_language=programming_language
    )
    return post


@pytest.fixture
def comment(db, user, post):
    """Creates a comment for testing."""
    comment = Comment.objects.create(
        author=user,
        post=post,
        content='Test comment content'
    )
    return comment


@pytest.fixture
def post_like(db, user, post):
    """Creates a post like for testing."""
    like = PostLike.objects.create(user=user, post=post)
    return like


@pytest.fixture
def comment_like(db, user, comment):
    """Creates a comment like for testing."""
    like = CommentLike.objects.create(user=user, comment=comment)
    return like


@pytest.fixture
def project(db, user, skill):
    """Creates a project for testing."""
    project = Project.objects.create(
        creator=user,
        title='Test Project',
        description='This is a test project',
        repository_url='https://github.com/testuser/test-project',
        status='active'
    )
    project.tech_stack.add(skill)
    ProjectCollaborator.objects.create(project=project, user=user, role='creator')
    return project


@pytest.fixture
def collaboration_request(db, another_user, project):
    """Creates a collaboration request for testing."""
    request = CollaborationRequest.objects.create(
        user=another_user,
        project=project,
        message='I would like to collaborate on this project',
        status='pending'
    )
    return request


@pytest.fixture
def notification(db, user, another_user):
    """Creates a notification for testing."""
    from django.contrib.contenttypes.models import ContentType
    from posts.models import Post
    
    # Create a related object (post)
    post = Post.objects.create(author=user, content="Test post content")
    content_type = ContentType.objects.get_for_model(post)
    
    notification = Notification.objects.create(
        recipient=user,
        sender=another_user,
        type='follow',
        text=f"{another_user.username} started following you.",
        is_read=False,
        content_type=content_type,
        object_id=post.id
    )
    return notification 