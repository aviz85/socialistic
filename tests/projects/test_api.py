import pytest
from django.urls import reverse
from rest_framework import status
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from tests.factories import ProjectFactory, SkillFactory, UserFactory

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
        assert len(response.data) == 2 or len(response.data['results']) == 2  # Handle pagination
        
        # If response has pagination
        projects_data = response.data['results'] if 'results' in response.data else response.data
        
        # Check that projects are in the response
        project_ids = [project['id'] for project in projects_data]
        assert project1.id in project_ids
        assert project2.id in project_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_project(self, auth_client, user):
        """Test creating a project."""
        # Create skills for tech stack
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        
        url = reverse('project-list')
        
        data = {
            'title': 'Test Project',
            'description': 'A test project description',
            'repo_url': 'https://github.com/testuser/test-project',
            'tech_stack_ids': [skill1.id, skill2.id]
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Test Project'
        assert response.data['description'] == 'A test project description'
        assert response.data['repo_url'] == 'https://github.com/testuser/test-project'
        assert response.data['creator']['id'] == user.id
        
        # Check that the project was created in the database
        project = Project.objects.get(id=response.data['id'])
        assert project.title == 'Test Project'
        assert project.description == 'A test project description'
        assert project.creator == user
        
        # Check that the creator was added as a collaborator
        assert ProjectCollaborator.objects.filter(project=project, user=user).exists()
        
        # Check that the skills were added to the tech stack
        assert skill1 in project.tech_stack.all()
        assert skill2 in project.tech_stack.all()

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_project_without_authentication(self, api_client):
        """Test that an unauthenticated user cannot create a project."""
        url = reverse('project-list')
        
        data = {
            'title': 'Test Project',
            'description': 'A test project description'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_project_without_title(self, auth_client):
        """Test that a project requires a title."""
        url = reverse('project-list')
        
        data = {
            'description': 'A test project description'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProjectDetailAPI:
    """Tests for project detail API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_retrieve_project(self, auth_client, user):
        """Test retrieving a project."""
        # Create skills for tech stack
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        
        # Create project with tech stack
        project = ProjectFactory(creator=user)
        project.tech_stack.add(skill1, skill2)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == project.id
        assert response.data['title'] == project.title
        assert response.data['description'] == project.description
        assert response.data['creator']['id'] == user.id
        
        # Check tech stack in response
        tech_stack_ids = [skill['id'] for skill in response.data['tech_stack']]
        assert skill1.id in tech_stack_ids
        assert skill2.id in tech_stack_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_update_own_project(self, auth_client, user):
        """Test updating own project."""
        project = ProjectFactory(creator=user)
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        data = {
            'title': 'Updated Project Title',
            'description': 'Updated project description',
            'repo_url': 'https://github.com/testuser/updated-project'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Project Title'
        assert response.data['description'] == 'Updated project description'
        assert response.data['repo_url'] == 'https://github.com/testuser/updated-project'
        
        # Check that the project was updated in the database
        project.refresh_from_db()
        assert project.title == 'Updated Project Title'
        assert project.description == 'Updated project description'
        assert project.repo_url == 'https://github.com/testuser/updated-project'

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


class TestProjectTechStackAPI:
    """Tests for project tech stack API."""
    
    @pytest.mark.skip("Tech stack endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_add_skills_to_tech_stack(self, auth_client, user):
        """Test adding skills to a project's tech stack."""
        project = ProjectFactory(creator=user)
        
        # Create skills to add
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        
        url = reverse('project-tech-stack', kwargs={'pk': project.id})
        data = {
            'skill_ids': [skill1.id, skill2.id]
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the skills were added in the database
        project.refresh_from_db()
        assert skill1 in project.tech_stack.all()
        assert skill2 in project.tech_stack.all()

    @pytest.mark.skip("Tech stack endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_remove_skill_from_tech_stack(self, auth_client, user):
        """Test removing a skill from a project's tech stack."""
        project = ProjectFactory(creator=user)
        
        # Add skills to tech stack
        skill1 = SkillFactory(name='Python')
        skill2 = SkillFactory(name='Django')
        project.tech_stack.add(skill1, skill2)
        
        url = reverse('project-remove-skill', kwargs={'pk': project.id, 'skill_id': skill1.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the skill was removed in the database
        project.refresh_from_db()
        assert skill1 not in project.tech_stack.all()
        assert skill2 in project.tech_stack.all()

    @pytest.mark.skip("Tech stack endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_modify_tech_stack_of_other_user_project(self, auth_client, another_user):
        """Test that a user cannot modify the tech stack of another user's project."""
        project = ProjectFactory(creator=another_user)
        
        # Create skill to add
        skill = SkillFactory(name='Python')
        
        url = reverse('project-tech-stack', kwargs={'pk': project.id})
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
        """Test requesting to collaborate on a project."""
        # Create a project by another user
        project = ProjectFactory(creator=another_user)
        
        url = reverse('project-collaborate', kwargs={'pk': project.id})
        data = {
            'message': 'I would like to collaborate on this project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user_id'] == user.id
        assert response.data['project'] == project.id
        assert response.data['message'] == 'I would like to collaborate on this project.'
        assert response.data['status'] == 'pending'
        
        # Check that the collaboration request was created in the database
        assert CollaborationRequest.objects.filter(
            user=user,
            project=project,
            message='I would like to collaborate on this project.',
            status='pending'
        ).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_request_collaboration_on_own_project(self, auth_client, user):
        """Test that a user cannot request to collaborate on their own project."""
        project = ProjectFactory(creator=user)
        
        url = reverse('project-collaborate', kwargs={'pk': project.id})
        data = {
            'message': 'I would like to collaborate on my own project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_request_collaboration_if_already_collaborator(self, auth_client, user, another_user):
        """Test that a user cannot request to collaborate if already a collaborator."""
        # Create a project by another user
        project = ProjectFactory(creator=another_user)
        
        # Add user as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=user
        )
        
        url = reverse('project-collaborate', kwargs={'pk': project.id})
        data = {
            'message': 'I would like to collaborate again on this project.'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.api
    @pytest.mark.integration
    def test_list_collaboration_requests(self, auth_client, user):
        """Test listing collaboration requests for user's projects."""
        # Create some projects for the user
        project1 = ProjectFactory(creator=user)
        project2 = ProjectFactory(creator=user)
        
        # Create some collaboration requests for user's projects
        request1 = CollaborationRequest.objects.create(
            user=UserFactory(),
            project=project1,
            message='Request 1'
        )
        request2 = CollaborationRequest.objects.create(
            user=UserFactory(),
            project=project2,
            message='Request 2'
        )
        
        # Create a collaboration request for another user's project
        another_project = ProjectFactory(creator=UserFactory())
        CollaborationRequest.objects.create(
            user=user,
            project=another_project,
            message='Request 3'
        )
        
        url = reverse('collaboration-requests')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2 or len(response.data['results']) == 2  # Handle pagination
        
        # If response has pagination
        requests_data = response.data['results'] if 'results' in response.data else response.data
        
        # Check that requests for user's projects are in the response
        request_ids = [req['id'] for req in requests_data]
        assert request1.id in request_ids
        assert request2.id in request_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_accept_collaboration_request(self, auth_client, user, another_user):
        """Test accepting a collaboration request."""
        # Create a project for the user
        project = ProjectFactory(creator=user)
        
        # Create a collaboration request from another user
        request = CollaborationRequest.objects.create(
            user=another_user,
            project=project,
            message='I would like to collaborate on this project.'
        )
        
        url = reverse('collaboration-request-respond', kwargs={'pk': request.id})
        data = {
            'status': 'accepted'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'approved'
        
        # Check that the request was updated in the database
        request.refresh_from_db()
        assert request.status == 'approved'
        
        # Check that the user was added as a collaborator
        assert ProjectCollaborator.objects.filter(project=project, user=another_user).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_reject_collaboration_request(self, auth_client, user, another_user):
        """Test rejecting a collaboration request."""
        # Create a project for the user
        project = ProjectFactory(creator=user)
        
        # Create a collaboration request from another user
        request = CollaborationRequest.objects.create(
            user=another_user,
            project=project,
            message='I would like to collaborate on this project.'
        )
        
        url = reverse('collaboration-request-respond', kwargs={'pk': request.id})
        data = {
            'status': 'rejected'
        }
        
        response = auth_client.post(url, data)
        
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
        # Create a project for another user
        project = ProjectFactory(creator=another_user)
        
        # Create a collaboration request
        request = CollaborationRequest.objects.create(
            user=UserFactory(),
            project=project,
            message='I would like to collaborate on this project.'
        )
        
        url = reverse('collaboration-request-respond', kwargs={'pk': request.id})
        data = {
            'status': 'accepted'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProjectCollaboratorsAPI:
    """Tests for project collaborators API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_list_project_collaborators(self, auth_client, user, another_user):
        """Test listing collaborators for a project."""
        # Create a project
        project = ProjectFactory(creator=user)
        
        # Add another user as a collaborator
        ProjectCollaborator.objects.create(
            project=project,
            user=another_user,
            role='contributor'
        )
        
        url = reverse('project-detail', kwargs={'pk': project.id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that both collaborators are in the response
        collaborator_ids = [collab['user']['id'] for collab in response.data['collaborators']]
        assert user.id in collaborator_ids
        assert another_user.id in collaborator_ids

    @pytest.mark.skip("Project leave endpoint needs to be checked")
    @pytest.mark.api
    @pytest.mark.integration
    def test_remove_collaborator(self, auth_client, user, another_user):
        """Test removing a collaborator from a project."""
        # Create a project
        project = ProjectFactory(creator=user)
        
        # Add another user as a collaborator
        collaborator = ProjectCollaborator.objects.create(
            project=project,
            user=another_user,
            role='contributor'
        )
        
        url = reverse('project-leave', kwargs={'pk': project.id, 'user_id': another_user.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the collaborator was removed from the database
        assert not ProjectCollaborator.objects.filter(id=collaborator.id).exists()

    @pytest.mark.skip("Project leave endpoint needs to be checked")
    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_remove_project_creator(self, auth_client, user):
        """Test that the project creator cannot be removed as a collaborator."""
        # Create a project
        project = ProjectFactory(creator=user)
        
        url = reverse('project-leave', kwargs={'pk': project.id, 'user_id': user.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check that the creator is still a collaborator
        assert ProjectCollaborator.objects.filter(project=project, user=user).exists()

    @pytest.mark.skip("Project leave endpoint needs to be checked")
    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_remove_collaborator_from_other_user_project(self, auth_client, another_user):
        """Test that a user cannot remove a collaborator from another user's project."""
        # Create a project for another user
        project = ProjectFactory(creator=another_user)
        
        # Add a third user as a collaborator
        third_user = UserFactory()
        ProjectCollaborator.objects.create(
            project=project,
            user=third_user,
            role='contributor'
        )
        
        url = reverse('project-leave', kwargs={'pk': project.id, 'user_id': third_user.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN 