from django.urls import path
from posts.views.posts import (
    PostListCreateView, PostDetailView, PostLikeView, PostUnlikeView, PostCommentsView
)
from posts.views.comments import (
    CommentListCreateView, CommentDetailView, CommentLikeView
)
from posts.views.search import PostSearchView

urlpatterns = [
    # Posts
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    path('<int:pk>/unlike/', PostUnlikeView.as_view(), name='post-unlike'),
    path('<int:pk>/comments/', PostCommentsView.as_view(), name='post-comments'),
    
    # Comments
    path('<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/like/', CommentLikeView.as_view(), name='comment-like'),
    
    # Search
    path('search/', PostSearchView.as_view(), name='post-search'),
] 