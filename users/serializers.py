from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Skill, ProgrammingLanguage, Follow

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']


class ProgrammingLanguageSerializer(serializers.ModelSerializer):
    """Serializer for programming languages."""
    
    class Meta:
        model = ProgrammingLanguage
        fields = ['id', 'name', 'icon']


class UserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'bio', 'profile_image',
            'github_profile', 'stackoverflow_profile', 'skills',
            'followers_count', 'following_count', 'is_following', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'created_at']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'password', 'confirm_password'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        # Validate that passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(_("Passwords don't match"))
        return data
    
    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password')
        
        # Create user with create_user method to properly handle password hashing
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, required=False)
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'full_name', 'bio', 'profile_image', 
            'github_profile', 'stackoverflow_profile', 'skills',
            'current_password', 'new_password', 'confirm_new_password'
        ]
    
    def validate(self, data):
        # Check if user is trying to change password
        if 'new_password' in data or 'confirm_new_password' in data or 'current_password' in data:
            # All password fields must be provided together
            if not all(field in data for field in ['new_password', 'confirm_new_password', 'current_password']):
                raise serializers.ValidationError(_("All password fields are required when changing password"))
            
            # Verify the current password
            if not self.instance.check_password(data['current_password']):
                raise serializers.ValidationError(_("Current password is incorrect"))
            
            # Check that new passwords match
            if data['new_password'] != data['confirm_new_password']:
                raise serializers.ValidationError(_("New passwords don't match"))
                
        return data
    
    def update(self, instance, validated_data):
        # Handle password change if requested
        if 'new_password' in validated_data:
            instance.set_password(validated_data['new_password'])
            # Remove password fields from validated_data
            validated_data.pop('new_password', None)
            validated_data.pop('confirm_new_password', None)
            validated_data.pop('current_password', None)
        
        # Handle skills if provided
        skills = validated_data.pop('skills', None)
        if skills is not None:
            instance.skills.set(skills)
        
        # Update the rest of the fields
        return super().update(instance, validated_data) 