from rest_framework import generics, permissions
from posts.models import Post
from posts.serializers import PostSerializer
from django.db.models import Q

class PostSearchView(generics.ListAPIView):
    """
    API endpoint for searching posts.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Post.objects.all()
        query = self.request.query_params.get('q', None)
        
        if query:
            queryset = queryset.filter(
                Q(content__icontains=query) |
                Q(code_snippet__icontains=query) |
                Q(author__username__icontains=query)
            )
        
        return queryset 