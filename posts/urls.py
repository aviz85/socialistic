from django.urls import path
from posts.views.posts import (
    PostListCreateView, PostDetailView, PostLikeView,
    PostUnlikeView, PostCommentsView
)

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    path('<int:pk>/unlike/', PostUnlikeView.as_view(), name='post-unlike'),
    path('<int:pk>/comments/', PostCommentsView.as_view(), name='post-comments'),
] 