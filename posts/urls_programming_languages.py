from django.urls import path
from posts.views.programming_languages import ProgrammingLanguageListView

urlpatterns = [
    path('', ProgrammingLanguageListView.as_view(), name='programming-language-list'),
] 