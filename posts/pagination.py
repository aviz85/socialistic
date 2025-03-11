from rest_framework.pagination import CursorPagination

class CustomCursorPagination(CursorPagination):
    """
    Custom cursor pagination that uses created_at field instead of created.
    """
    ordering = '-created_at' 