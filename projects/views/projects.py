from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from projects.models import Project, ProjectCollaborator, CollaborationRequest
from projects.serializers import (
    ProjectSerializer, ProjectCollaboratorSerializer, 
    CollaborationRequestSerializer
)
from notifications.models import Notification


class IsProjectCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of a project to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the creator
        return obj.creator == request.user


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.all()


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a project.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectCreatorOrReadOnly]


class ProjectCollaborateView(APIView):
    """
    API endpoint for requesting to collaborate on a project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Check if already a collaborator
        if ProjectCollaborator.objects.filter(user=request.user, project=project).exists():
            return Response(
                {"detail": "You are already a collaborator on this project."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already requested
        if CollaborationRequest.objects.filter(
            user=request.user, project=project, status='pending'
        ).exists():
            return Response(
                {"detail": "You have already requested to collaborate on this project."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create collaboration request
        message = request.data.get('message', '')
        collaboration_request = CollaborationRequest.objects.create(
            user=request.user,
            project=project,
            message=message
        )
        
        # Create notification
        Notification.objects.create(
            recipient=project.creator,
            sender=request.user,
            type='project_request',
            content_type=ContentType.objects.get_for_model(CollaborationRequest),
            object_id=collaboration_request.id,
            text=f"{request.user.username} requested to collaborate on {project.title}"
        )
        
        return Response(
            CollaborationRequestSerializer(collaboration_request).data,
            status=status.HTTP_201_CREATED
        )


class ProjectLeaveView(APIView):
    """
    API endpoint for leaving a project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Check if a collaborator
        collaborator = get_object_or_404(
            ProjectCollaborator, user=request.user, project=project
        )
        
        # Can't leave if you're the owner
        if collaborator.role == 'owner':
            return Response(
                {"detail": "Project owners cannot leave. Transfer ownership first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove from project
        collaborator.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollaborationRequestListView(generics.ListAPIView):
    """
    API endpoint for listing collaboration requests for projects created by the user.
    """
    serializer_class = CollaborationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Get all pending requests for projects created by the user
        return CollaborationRequest.objects.filter(
            project__creator=self.request.user,
            status='pending'
        )


class CollaborationRequestResponseView(APIView):
    """
    API endpoint for responding to a collaboration request.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        collaboration_request = get_object_or_404(CollaborationRequest, pk=pk)
        
        # Only the project creator can respond
        if collaboration_request.project.creator != request.user:
            return Response(
                {"detail": "Only the project creator can respond to collaboration requests."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the response (accepted/rejected)
        response_status = request.data.get('status', '').lower()
        if response_status not in ['accepted', 'rejected']:
            return Response(
                {"detail": "Status must be either 'accepted' or 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if response_status == 'accepted':
            # Use the accept method
            collaboration_request.accept()
            
            # Create notification
            Notification.objects.create(
                recipient=collaboration_request.user,
                sender=request.user,
                type='project_accepted',
                content_type=ContentType.objects.get_for_model(Project),
                object_id=collaboration_request.project.id,
                text=f"Your request to join {collaboration_request.project.title} was approved"
            )
        else:
            # Use the reject method
            collaboration_request.reject()
            
            # Create notification for rejection
            Notification.objects.create(
                recipient=collaboration_request.user,
                sender=request.user,
                type='project_rejected',
                content_type=ContentType.objects.get_for_model(Project),
                object_id=collaboration_request.project.id,
                text=f"Your request to join {collaboration_request.project.title} was rejected"
            )
        
        return Response(
            CollaborationRequestSerializer(collaboration_request).data,
            status=status.HTTP_200_OK
        ) 