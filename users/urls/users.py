from django.urls import path
from users.views.users import (
    UserListView, UserDetailView, UserPostsView, UserProjectsView,
    UserFollowView, UserUnfollowView, UserFollowersView, UserFollowingView
)

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/posts/', UserPostsView.as_view(), name='user-posts'),
    path('<int:pk>/projects/', UserProjectsView.as_view(), name='user-projects'),
    path('<int:pk>/follow/', UserFollowView.as_view(), name='user-follow'),
    path('<int:pk>/unfollow/', UserUnfollowView.as_view(), name='user-unfollow'),
    path('<int:pk>/followers/', UserFollowersView.as_view(), name='user-followers'),
    path('<int:pk>/following/', UserFollowingView.as_view(), name='user-following'),
] 