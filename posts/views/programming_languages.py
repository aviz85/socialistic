from rest_framework import generics
from rest_framework.permissions import AllowAny
from users.models import ProgrammingLanguage
from users.serializers import ProgrammingLanguageSerializer
from rest_framework.pagination import PageNumberPagination

class ProgrammingLanguagePagination(PageNumberPagination):
    """
    Custom pagination for programming languages.
    """
    page_size = 100  # Show more languages per page since there won't be many

class ProgrammingLanguageListView(generics.ListAPIView):
    """
    API endpoint to list all programming languages.
    """
    queryset = ProgrammingLanguage.objects.all().order_by('name')
    serializer_class = ProgrammingLanguageSerializer
    permission_classes = [AllowAny]
    pagination_class = ProgrammingLanguagePagination