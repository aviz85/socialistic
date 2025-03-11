from django.urls import path
from users.views.search import UserSearchView
from posts.views.search import PostSearchView
from projects.views.search import ProjectSearchView

urlpatterns = [
    path('users/', UserSearchView.as_view(), name='search-users'),
    path('posts/', PostSearchView.as_view(), name='search-posts'),
    path('projects/', ProjectSearchView.as_view(), name='search-projects'),
] 