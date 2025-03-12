"""
URL configuration for socialistic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import RedirectView

# Swagger schema view
schema_view = get_schema_view(
   openapi.Info(
      title="Socialistic API",
      default_version='v1',
      description="API documentation for the Socialistic developer social network",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@socialistic.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation with Swagger
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/auth/', include('users.urls.auth')),
    path('api/users/', include('users.urls.users')),
    path('api/posts/', include('posts.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/search/', include('socialistic.urls_search')),
    path('api/programming-languages/', include('posts.urls_programming_languages')),
    
    # Frontend
    path('', RedirectView.as_view(url='/static/frontend/index.html'), name='home'),
    # React app catch-all route to allow React Router to handle client-side routing
    path('app/<path:path>', RedirectView.as_view(url='/static/frontend/index.html'), name='react-routes'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Serve files from STATICFILES_DIRS for development
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
