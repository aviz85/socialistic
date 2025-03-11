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

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an unauthenticated API client for testing API views."""
    return APIClient()


@pytest.fixture
def auth_client(user):
    """Return an authenticated API client for the default test user."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def user():
    """Return a default test user."""
    return User.objects.create_user(
        email='testuser@example.com',
        username='testuser',
        password='testpassword',
        full_name='Test User'
    )


@pytest.fixture
def admin_user():
    """Return an admin user for testing."""
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='adminpassword'
    )


@pytest.fixture
def another_user():
    """Return a second test user for follow/interactions testing."""
    return User.objects.create_user(
        email='another@example.com',
        username='anotheruser',
        password='testpassword',
        full_name='Another User'
    )


@pytest.fixture
def programming_language():
    """Return a test programming language."""
    return ProgrammingLanguage.objects.create(name='Python')


@pytest.fixture
def skill():
    """Return a test skill."""
    return Skill.objects.create(name='Django', category='backend')


@pytest.fixture
def skills_set():
    """Return a set of test skills."""
    return [
        Skill.objects.create(name='React', category='frontend'),
        Skill.objects.create(name='Node.js', category='backend'),
        Skill.objects.create(name='Docker', category='devops')
    ]


@pytest.fixture
def follow_relationship(user, another_user):
    """Create a follow relationship between users."""
    return Follow.objects.create(follower=user, following=another_user)


@pytest.fixture
def post(user, programming_language):
    """Return a test post."""
    return Post.objects.create(
        author=user,
        content='Test post content',
        code_snippet='print("Hello, World!")',
        programming_language=programming_language
    )


@pytest.fixture
def comment(post, another_user):
    """Return a test comment."""
    return Comment.objects.create(
        author=another_user,
        post=post,
        content='Test comment'
    )


@pytest.fixture
def post_like(post, another_user):
    """Return a test post like."""
    return PostLike.objects.create(user=another_user, post=post)


@pytest.fixture
def comment_like(comment, user):
    """Return a test comment like."""
    return CommentLike.objects.create(user=user, comment=comment)


@pytest.fixture
def project(user, skills_set):
    """Return a test project."""
    project = Project.objects.create(
        creator=user,
        title='Test Project',
        description='Test project description',
        repo_url='https://github.com/test/project'
    )
    project.tech_stack.add(*skills_set)
    ProjectCollaborator.objects.create(
        user=user,
        project=project,
        role='owner'
    )
    return project


@pytest.fixture
def collaboration_request(project, another_user):
    """Return a test collaboration request."""
    return CollaborationRequest.objects.create(
        user=another_user,
        project=project,
        message='I would like to collaborate'
    )


@pytest.fixture
def notification(user, another_user, post):
    """Return a test notification."""
    return Notification.objects.create(
        recipient=user,
        sender=another_user,
        type='like',
        content_type=ContentType.objects.get_for_model(Post),
        object_id=post.id,
        text=f"{another_user.username} liked your post"
    ) 