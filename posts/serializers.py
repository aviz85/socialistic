from rest_framework import serializers
from .models import Post, Comment, PostLike, CommentLike
from users.serializers import UserSerializer, ProgrammingLanguageSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'created_at', 
            'updated_at', 'likes_count', 'is_liked'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommentLike.objects.filter(user=request.user, comment=obj).exists()
        return False


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    programming_language = ProgrammingLanguageSerializer(read_only=True)
    programming_language_id = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammingLanguageSerializer.Meta.model.objects.all(),
        write_only=True,
        required=False,
        source='programming_language'
    )
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'code_snippet', 
            'programming_language', 'programming_language_id',
            'created_at', 'updated_at', 'likes_count', 
            'comments_count', 'is_liked'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False
    
    def create(self, validated_data):
        # Set the author to the current user
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data) 