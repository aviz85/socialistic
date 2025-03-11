from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from users.serializers import UserSerializer
from posts.serializers import PostSerializer
from projects.serializers import ProjectSerializer
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification

User = get_user_model()


class UserListView(generics.ListAPIView):
    """
    API endpoint for listing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserPostsView(generics.ListAPIView):
    """
    API endpoint for listing a user's posts.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return user.posts.all()


class UserProjectsView(generics.ListAPIView):
    """
    API endpoint for listing a user's projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return user.created_projects.all()


class UserFollowView(APIView):
    """
    API endpoint for following a user.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        user_to_follow = get_object_or_404(User, pk=pk)
        
        # Can't follow yourself
        if request.user == user_to_follow:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Follow the user
        request.user.follow(user_to_follow)
        
        # Create notification
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            type='follow',
            content_type=ContentType.objects.get_for_model(User),
            object_id=user_to_follow.id,
            text=f"{request.user.username} started following you"
        )
        
        return Response(status=status.HTTP_201_CREATED)


class UserUnfollowView(APIView):
    """
    API endpoint for unfollowing a user.
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        user_to_unfollow = get_object_or_404(User, pk=pk)
        
        # Unfollow the user
        request.user.unfollow(user_to_unfollow)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFollowersView(generics.ListAPIView):
    """
    API endpoint for listing a user's followers.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return User.objects.filter(following__following=user)


class UserFollowingView(generics.ListAPIView):
    """
    API endpoint for listing users that a user is following.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return User.objects.filter(followers__follower=user) 