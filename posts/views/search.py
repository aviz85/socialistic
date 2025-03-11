from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from posts.models import Post
from posts.serializers import PostSerializer
from users.models import ProgrammingLanguage


class PostSearchView(generics.ListAPIView):
    """
    API endpoint for searching posts.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['content', 'code_snippet']
    
    def get_queryset(self):
        queryset = Post.objects.all()
        
        # Filter by programming language if provided
        language_id = self.request.query_params.get('language')
        if language_id:
            try:
                language = ProgrammingLanguage.objects.get(id=language_id)
                queryset = queryset.filter(programming_language=language)
            except ProgrammingLanguage.DoesNotExist:
                pass
        
        # Filter by has_code if provided
        has_code = self.request.query_params.get('has_code')
        if has_code == 'true':
            queryset = queryset.exclude(code_snippet='')
        
        return queryset 