from django.urls import path
from posts.views.posts import (
    PostListCreateView, PostDetailView, PostLikeView
)
from posts.views.comments import (
    CommentListCreateView, CommentDetailView, CommentLikeView
)
from posts.views.search import PostSearchView

urlpatterns = [
    # Posts
    path('', PostListCreateView.as_view(), name='post-list-create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    
    # Comments
    path('<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/like/', CommentLikeView.as_view(), name='comment-like'),
    
    # Search
    path('search/', PostSearchView.as_view(), name='post-search'),
] 