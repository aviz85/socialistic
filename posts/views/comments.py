from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from posts.models import Post, Comment, CommentLike
from posts.serializers import CommentSerializer
from notifications.models import Notification
from posts.pagination import CustomCursorPagination


class CommentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating comments on a post.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomCursorPagination
    
    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post.comments.all()
    
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = serializer.save(author=self.request.user, post=post)
        
        # Create notification (if not commenting on own post)
        if post.author != self.request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=self.request.user,
                type='comment',
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id,
                text=f"{self.request.user.username} commented on your post"
            )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        # Only allow the author to update the comment
        if serializer.instance.author != self.request.user:
            self.permission_denied(self.request)
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow the author to delete the comment
        if instance.author != self.request.user:
            self.permission_denied(self.request)
        instance.delete()


class CommentLikeView(APIView):
    """
    API endpoint for liking/unliking a comment.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        
        # Check if already liked
        if CommentLike.objects.filter(user=request.user, comment=comment).exists():
            return Response(
                {"detail": "You have already liked this comment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create like
        CommentLike.objects.create(user=request.user, comment=comment)
        
        # Create notification (if not liking own comment)
        if comment.author != request.user:
            Notification.objects.create(
                recipient=comment.author,
                sender=request.user,
                type='like',
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id,
                text=f"{request.user.username} liked your comment"
            )
        
        return Response(status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        
        # Delete like if exists
        CommentLike.objects.filter(user=request.user, comment=comment).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
