from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from users.serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        # Create regular token for frontend
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'token': token.key,
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    API endpoint for logout - blacklist the JWT token.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Blacklist JWT token if provided
            if 'refresh' in request.data:
                refresh_token = request.data["refresh"]
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Delete regular token if it exists
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
                
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserMe(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get or update the authenticated user.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that returns user data with tokens.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            # Get user from the provided credentials
            user = User.objects.get(email=request.data['email'])
            
            # Get or create regular token for frontend
            token, created = Token.objects.get_or_create(user=user)
            
            # Add user data and regular token to the response
            response.data['user'] = UserSerializer(user, context={'request': request}).data
            response.data['token'] = token.key
            
        return response 