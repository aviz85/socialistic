from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from projects.models import Project
from projects.serializers import ProjectSerializer
from users.models import Skill


class ProjectSearchView(generics.ListAPIView):
    """
    API endpoint for searching projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        queryset = Project.objects.all()
        
        # Filter by skill/tech stack if provided
        skill_id = self.request.query_params.get('skill')
        if skill_id:
            try:
                skill = Skill.objects.get(id=skill_id)
                queryset = queryset.filter(tech_stack=skill)
            except Skill.DoesNotExist:
                pass
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status in ['active', 'completed', 'on_hold']:
            queryset = queryset.filter(status=status)
        
        return queryset 