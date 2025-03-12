from rest_framework import serializers
from .models import Project, ProjectCollaborator, CollaborationRequest
from users.serializers import UserSerializer, SkillSerializer


class ProjectCollaboratorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectCollaborator
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class CollaborationRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = CollaborationRequest
        fields = ['id', 'user', 'user_id', 'project', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'user_id', 'project', 'status', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    tech_stack = SkillSerializer(many=True, read_only=True)
    tech_stack_ids = serializers.PrimaryKeyRelatedField(
        queryset=SkillSerializer.Meta.model.objects.all(),
        write_only=True,
        many=True,
        source='tech_stack'
    )
    collaborators_count = serializers.IntegerField(read_only=True)
    is_collaborator = serializers.SerializerMethodField()
    collaborators = ProjectCollaboratorSerializer(
        source='projectcollaborator_set',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = Project
        fields = [
            'id', 'creator', 'title', 'description', 'repo_url',
            'tech_stack', 'tech_stack_ids', 'status', 'created_at',
            'updated_at', 'collaborators_count', 'is_collaborator',
            'collaborators'
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']
    
    def get_is_collaborator(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProjectCollaborator.objects.filter(
                user=request.user, project=obj
            ).exists()
        return False
    
    def create(self, validated_data):
        # Set the creator to the current user
        validated_data['creator'] = self.context['request'].user
        
        # Create the project
        project = super().create(validated_data)
        
        # The Project model's save method already adds the creator as owner collaborator
        
        return project 