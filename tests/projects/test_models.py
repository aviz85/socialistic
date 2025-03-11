import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from tests.factories import UserFactory, ProjectFactory, SkillFactory

pytestmark = pytest.mark.django_db


class TestProjectModel:
    """Unit tests for the Project model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_project_creation(self, user):
        """Test creating a project."""
        project = Project.objects.create(
            creator=user,
            title='Test Project',
            description='A test project description',
            repository_url='https://github.com/testuser/test-project'
        )
        
        assert project.creator == user
        assert project.title == 'Test Project'
        assert project.description == 'A test project description'
        assert project.repository_url == 'https://github.com/testuser/test-project'
        assert project.status == 'active'
        assert project.created_at <= timezone.now()
        assert project.updated_at <= timezone.now()
        
        # Check that the creator is automatically added as a collaborator
        assert project.collaborators.count() == 1
        assert project.collaborators.first() == user

    @pytest.mark.unit
    @pytest.mark.model
    def test_project_str(self, user):
        """Test the string representation of a project."""
        project = ProjectFactory(creator=user, title='Test Project')
        assert str(project) == 'Test Project'

    @pytest.mark.unit
    @pytest.mark.model
    def test_add_tech_stack(self, user):
        """Test adding skills to a project's tech stack."""
        project = ProjectFactory(creator=user)
        
        # Create skills to add
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        
        # Add skills to tech stack
        project.tech_stack.add(skill1, skill2)
        
        # Check that the skills are in the tech stack
        assert project.tech_stack.count() == 2
        assert skill1 in project.tech_stack.all()
        assert skill2 in project.tech_stack.all()

    @pytest.mark.unit
    @pytest.mark.model
    def test_project_requires_creator(self):
        """Test that a project requires a creator."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Project.objects.create(
                    title='Test Project',
                    description='A test project description'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_project_requires_title(self, user):
        """Test that a project requires a title."""
        with pytest.raises(ValidationError):
            project = Project(creator=user, title='', description='A test project description')
            project.clean()

    @pytest.mark.unit
    @pytest.mark.model
    def test_repository_url_valid_format(self, user):
        """Test that repository_url must be a valid URL format if provided."""
        with pytest.raises(ValidationError):
            project = Project(
                creator=user,
                title='Test Project',
                description='A test project description',
                repository_url='not_a_url'
            )
            project.clean()
        
        # Valid URL should pass
        project = Project(
            creator=user,
            title='Test Project',
            description='A test project description',
            repository_url='https://github.com/testuser/test-project'
        )
        project.clean()


class TestProjectCollaboratorModel:
    """Unit tests for the ProjectCollaborator model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_collaborator_creation(self, user, another_user):
        """Test creating a collaborator."""
        project = ProjectFactory(creator=user)
        
        collaborator = ProjectCollaborator.objects.create(
            project=project,
            user=another_user
        )
        
        assert collaborator.project == project
        assert collaborator.user == another_user
        assert collaborator.created_at <= timezone.now()

    @pytest.mark.unit
    @pytest.mark.model
    def test_collaborator_str(self, user, another_user):
        """Test the string representation of a collaborator."""
        project = ProjectFactory(creator=user, title='Test Project')
        collaborator = ProjectCollaborator.objects.create(
            project=project,
            user=another_user
        )
        
        expected_str = f"{another_user.username} on {project.title}"
        assert str(collaborator) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_unique_collaborator_constraint(self, user, another_user):
        """Test that a user can only be a collaborator on a project once."""
        project = ProjectFactory(creator=user)
        
        # Creator is already a collaborator by default
        # Try to add the creator again
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                ProjectCollaborator.objects.create(
                    project=project,
                    user=user
                )
        
        # Add another user as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=another_user
        )
        
        # Try to add the same user again
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                ProjectCollaborator.objects.create(
                    project=project,
                    user=another_user
                )


class TestCollaborationRequestModel:
    """Unit tests for the CollaborationRequest model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_collaboration_request_creation(self, user, another_user):
        """Test creating a collaboration request."""
        project = ProjectFactory(creator=another_user)
        
        request = CollaborationRequest.objects.create(
            project=project,
            user=user,
            message='I would like to collaborate on this project.'
        )
        
        assert request.project == project
        assert request.user == user
        assert request.message == 'I would like to collaborate on this project.'
        assert request.status == 'pending'
        assert request.created_at <= timezone.now()
        assert request.updated_at <= timezone.now()

    @pytest.mark.unit
    @pytest.mark.model
    def test_collaboration_request_str(self, user, another_user):
        """Test the string representation of a collaboration request."""
        project = ProjectFactory(creator=another_user, title='Test Project')
        request = CollaborationRequest.objects.create(
            project=project,
            user=user,
            message='I would like to collaborate on this project.'
        )
        
        expected_str = f"{user.username} requests to join {project.title} (pending)"
        assert str(request) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_unique_request_constraint(self, user, another_user):
        """Test that a user can only have one active request per project."""
        project = ProjectFactory(creator=another_user)
        
        CollaborationRequest.objects.create(
            project=project,
            user=user,
            message='First request'
        )
        
        # Try to create another pending request
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                CollaborationRequest.objects.create(
                    project=project,
                    user=user,
                    message='Second request'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_cannot_request_own_project(self, user):
        """Test that a user cannot request to join their own project."""
        project = ProjectFactory(creator=user)
        
        with pytest.raises(ValidationError):
            request = CollaborationRequest(
                project=project,
                user=user,
                message='I want to join my own project'
            )
            request.clean()

    @pytest.mark.unit
    @pytest.mark.model
    def test_cannot_request_if_already_collaborator(self, user, another_user):
        """Test that a user cannot request to join a project they are already a collaborator on."""
        project = ProjectFactory(creator=another_user)
        
        # Add user as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=user
        )
        
        with pytest.raises(ValidationError):
            request = CollaborationRequest(
                project=project,
                user=user,
                message='I want to join again'
            )
            request.clean()

    @pytest.mark.unit
    @pytest.mark.model
    def test_accept_request(self, user, another_user):
        """Test accepting a collaboration request."""
        project = ProjectFactory(creator=another_user)
        
        request = CollaborationRequest.objects.create(
            project=project,
            user=user,
            message='I would like to collaborate on this project.'
        )
        
        request.accept()
        
        # Check that the request was updated
        assert request.status == 'accepted'
        
        # Check that the user was added as a collaborator
        assert ProjectCollaborator.objects.filter(project=project, user=user).exists()

    @pytest.mark.unit
    @pytest.mark.model
    def test_reject_request(self, user, another_user):
        """Test rejecting a collaboration request."""
        project = ProjectFactory(creator=another_user)
        
        request = CollaborationRequest.objects.create(
            project=project,
            user=user,
            message='I would like to collaborate on this project.'
        )
        
        request.reject()
        
        # Check that the request was updated
        assert request.status == 'rejected'
        
        # Check that the user was not added as a collaborator
        assert not ProjectCollaborator.objects.filter(project=project, user=user).exists() 