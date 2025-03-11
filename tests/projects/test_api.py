import pytest
from django.urls import reverse
from rest_framework import status
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from tests.factories import ProjectFactory, SkillFactory

pytestmark = pytest.mark.django_db


class TestProjectListCreateAPI:
    """Tests for project list and create API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_list_projects(self, auth_client, user, another_user):
        """Test listing projects."""
        # Create some projects
        project1 = ProjectFactory(creator=user)
        project2 = ProjectFactory(creator=another_user)
        
        url = reverse('project-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Assuming pagination is used
        
        # Check that both projects are in the response
        project_ids = [project['id'] for project in response.data['results']]
        assert project1.id in project_ids
        assert project2.id in project_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_project(self, auth_client, user):
        """Test creating a project."""
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'A new project description',
            'repository_url': 'https://github.com/testuser/new-project',
            'tech_stack': [skill1.id, skill2.id]
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Project'
        assert response.data['description'] == 'A new project description'
        assert response.data['repository_url'] == 'https://github.com/testuser/new-project'
        assert response.data['creator']['username'] == user.username
        assert len(response.data['tech_stack']) == 2
        
        # Check that the project was created in the database
        project = Project.objects.get(id=response.data['id'])
        assert project.title == 'New Project'
        assert project.creator == user
        assert project.tech_stack.count() == 2
        
        # Check that the user was added as a collaborator
        assert project.collaborators.count() == 1
        assert project.collaborators.first() == user

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_project_without_authentication(self, api_client):
        """Test that an unauthenticated user cannot create a project."""
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'A new project description'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_project_without_title(self, auth_client):
        """Test that creating a project without a title fails."""
        url = reverse('project-list')
        data = {
            'description': 'A new project description'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data


class TestProjectDetailAPI:
    """Tests for project detail API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_retrieve_project(self, auth_client, user):
        """Test retrieving a project."""
        project = ProjectFactory(creator=user)
        
        # Add skills to tech stack
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        project.tech_stack.add(skill1, skill2)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == project.id
        assert response.data['title'] == project.title
        assert response.data['creator']['username'] == user.username
        assert len(response.data['tech_stack']) == 2

    @pytest.mark.api
    @pytest.mark.integration
    def test_update_own_project(self, auth_client, user):
        """Test updating own project."""
        project = ProjectFactory(creator=user)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        data = {
            'title': 'Updated Project Title',
            'description': 'Updated project description'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Project Title'
        assert response.data['description'] == 'Updated project description'
        
        # Check that the project was updated in the database
        project.refresh_from_db()
        assert project.title == 'Updated Project Title'
        assert project.description == 'Updated project description'

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_update_other_user_project(self, auth_client, another_user):
        """Test that a user cannot update another user's project."""
        project = ProjectFactory(creator=another_user)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        data = {
            'title': 'Updated Project Title'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_own_project(self, auth_client, user):
        """Test deleting own project."""
        project = ProjectFactory(creator=user)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the project was deleted from the database
        assert not Project.objects.filter(id=project.id).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_delete_other_user_project(self, auth_client, another_user):
        """Test that a user cannot delete another user's project."""
        project = ProjectFactory(creator=another_user)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Check that the project was not deleted from the database
        assert Project.objects.filter(id=project.id).exists()


class TestProjectTechStackAPI:
    """Tests for project tech stack API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_add_skills_to_tech_stack(self, auth_client, user):
        """Test adding skills to a project's tech stack."""
        project = ProjectFactory(creator=user)
        
        # Create skills to add
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        
        url = reverse('project-tech-stack', kwargs={'project_id': project.id})
        data = {
            'skill_ids': [skill1.id, skill2.id]
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the skills were added in the database
        project.refresh_from_db()
        assert project.tech_stack.count() == 2
        assert skill1 in project.tech_stack.all()
        assert skill2 in project.tech_stack.all()

    @pytest.mark.api
    @pytest.mark.integration
    def test_remove_skill_from_tech_stack(self, auth_client, user):
        """Test removing a skill from a project's tech stack."""
        project = ProjectFactory(creator=user)
        
        # Add skills to tech stack
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        project.tech_stack.add(skill1, skill2)
        
        url = reverse('project-remove-skill', kwargs={'project_id': project.id, 'skill_id': skill1.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the skill was removed in the database
        project.refresh_from_db()
        assert project.tech_stack.count() == 1
        assert skill1 not in project.tech_stack.all()
        assert skill2 in project.tech_stack.all()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_modify_tech_stack_of_other_user_project(self, auth_client, another_user):
        """Test that a user cannot modify the tech stack of another user's project."""
        project = ProjectFactory(creator=another_user)
        
        # Create a skill to add
        skill = SkillFactory(name='Python')
        
        url = reverse('project-tech-stack', kwargs={'project_id': project.id})
        data = {
            'skill_ids': [skill.id]
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCollaborationRequestAPI:
    """Tests for collaboration request API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_request_collaboration(self, auth_client, user, another_user):
        """Test requesting collaboration on a project."""
        project = ProjectFactory(creator=another_user)
        
        url = reverse('project-request-collaboration', kwargs={'project_id': project.id})
        data = {
            'message': 'I would like to collaborate on this project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['project'] == project.id
        assert response.data['user']['username'] == user.username
        assert response.data['message'] == 'I would like to collaborate on this project.'
        assert response.data['status'] == 'pending'
        
        # Check that the request was created in the database
        assert CollaborationRequest.objects.filter(
            project=project,
            user=user,
            message='I would like to collaborate on this project.'
        ).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_request_collaboration_on_own_project(self, auth_client, user):
        """Test that a user cannot request collaboration on their own project."""
        project = ProjectFactory(creator=user)
        
        url = reverse('project-request-collaboration', kwargs={'project_id': project.id})
        data = {
            'message': 'I would like to collaborate on my own project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_request_collaboration_if_already_collaborator(self, auth_client, user, another_user):
        """Test that a user cannot request collaboration if already a collaborator."""
        project = ProjectFactory(creator=another_user)
        
        # Add user as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=user
        )
        
        url = reverse('project-request-collaboration', kwargs={'project_id': project.id})
        data = {
            'message': 'I would like to collaborate on this project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_collaboration_requests(self, auth_client, user):
        """Test listing collaboration requests for a project."""
        project = ProjectFactory(creator=user)
        
        # Create some collaboration requests
        user2 = UserFactory(username='user2')
        user3 = UserFactory(username='user3')
        
        request1 = CollaborationRequest.objects.create(
            project=project,
            user=user2,
            message='Request from user2'
        )
        
        request2 = CollaborationRequest.objects.create(
            project=project,
            user=user3,
            message='Request from user3'
        )
        
        url = reverse('project-collaboration-requests', kwargs={'project_id': project.id})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Check that both requests are in the response
        request_ids = [request['id'] for request in response.data]
        assert request1.id in request_ids
        assert request2.id in request_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_accept_collaboration_request(self, auth_client, user, another_user):
        """Test accepting a collaboration request."""
        project = ProjectFactory(creator=user)
        
        request = CollaborationRequest.objects.create(
            project=project,
            user=another_user,
            message='I would like to collaborate on this project.'
        )
        
        url = reverse('collaboration-request-accept', kwargs={'pk': request.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'accepted'
        
        # Check that the request was updated in the database
        request.refresh_from_db()
        assert request.status == 'accepted'
        
        # Check that the user was added as a collaborator
        assert ProjectCollaborator.objects.filter(project=project, user=another_user).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_reject_collaboration_request(self, auth_client, user, another_user):
        """Test rejecting a collaboration request."""
        project = ProjectFactory(creator=user)
        
        request = CollaborationRequest.objects.create(
            project=project,
            user=another_user,
            message='I would like to collaborate on this project.'
        )
        
        url = reverse('collaboration-request-reject', kwargs={'pk': request.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'rejected'
        
        # Check that the request was updated in the database
        request.refresh_from_db()
        assert request.status == 'rejected'
        
        # Check that the user was not added as a collaborator
        assert not ProjectCollaborator.objects.filter(project=project, user=another_user).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_accept_request_for_other_user_project(self, auth_client, user, another_user):
        """Test that a user cannot accept a request for another user's project."""
        project = ProjectFactory(creator=another_user)
        
        # Create a user for the request
        user2 = UserFactory(username='user2')
        
        request = CollaborationRequest.objects.create(
            project=project,
            user=user,
            message='I would like to collaborate on this project.'
        )
        
        url = reverse('collaboration-request-accept', kwargs={'pk': request.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProjectCollaboratorsAPI:
    """Tests for project collaborators API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_list_project_collaborators(self, auth_client, user, another_user):
        """Test listing collaborators for a project."""
        project = ProjectFactory(creator=user)
        
        # Add another user as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=another_user
        )
        
        url = reverse('project-collaborators', kwargs={'project_id': project.id})
        
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Creator and the added collaborator
        
        # Check that both collaborators are in the response
        usernames = [collaborator['username'] for collaborator in response.data]
        assert user.username in usernames
        assert another_user.username in usernames

    @pytest.mark.api
    @pytest.mark.integration
    def test_remove_collaborator(self, auth_client, user, another_user):
        """Test removing a collaborator from a project."""
        project = ProjectFactory(creator=user)
        
        # Add another user as a collaborator
        collaboration = ProjectCollaborator.objects.create(
            project=project,
            user=another_user
        )
        
        url = reverse('project-remove-collaborator', kwargs={'project_id': project.id, 'username': another_user.username})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the collaborator was removed from the database
        assert not ProjectCollaborator.objects.filter(id=collaboration.id).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_remove_project_creator(self, auth_client, user):
        """Test that the project creator cannot be removed as a collaborator."""
        project = ProjectFactory(creator=user)
        
        url = reverse('project-remove-collaborator', kwargs={'project_id': project.id, 'username': user.username})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the creator is still a collaborator
        assert ProjectCollaborator.objects.filter(project=project, user=user).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_remove_collaborator_from_other_user_project(self, auth_client, another_user):
        """Test that a user cannot remove a collaborator from another user's project."""
        project = ProjectFactory(creator=another_user)
        
        # Create a user to add as a collaborator
        user2 = UserFactory(username='user2')
        
        # Add user2 as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=user2
        )
        
        url = reverse('project-remove-collaborator', kwargs={'project_id': project.id, 'username': user2.username})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Check that the collaborator was not removed
        assert ProjectCollaborator.objects.filter(project=project, user=user2).exists() 