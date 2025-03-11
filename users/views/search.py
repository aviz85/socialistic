from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from users.serializers import UserSerializer
from users.models import Skill

User = get_user_model()


class UserSearchView(generics.ListAPIView):
    """
    API endpoint for searching users.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'full_name', 'bio']
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter by skill if provided
        skill_id = self.request.query_params.get('skill')
        if skill_id:
            try:
                skill = Skill.objects.get(id=skill_id)
                queryset = queryset.filter(skills=skill)
            except Skill.DoesNotExist:
                pass
        
        # Filter by GitHub profile if provided
        has_github = self.request.query_params.get('has_github')
        if has_github == 'true':
            queryset = queryset.exclude(github_profile='')
        
        # Filter by StackOverflow profile if provided
        has_stackoverflow = self.request.query_params.get('has_stackoverflow')
        if has_stackoverflow == 'true':
            queryset = queryset.exclude(stackoverflow_profile='')
        
        return queryset 