import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from posts.models import Post, Comment, PostLike, CommentLike
from tests.factories import UserFactory, PostFactory, CommentFactory, PostLikeFactory, CommentLikeFactory, ProgrammingLanguageFactory

pytestmark = pytest.mark.django_db


class TestPostModel:
    """Unit tests for the Post model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_creation(self, user):
        """Test creating a post."""
        language = ProgrammingLanguageFactory(name='Python')
        post = Post.objects.create(
            author=user,
            content='Test post content',
            code_snippet='print("Hello, world!")',
            programming_language=language
        )
        
        assert post.author == user
        assert post.content == 'Test post content'
        assert post.code_snippet == 'print("Hello, world!")'
        assert post.programming_language == language
        assert post.created_at <= timezone.now()
        assert post.updated_at <= timezone.now()
        assert post.likes_count == 0
        assert post.comments_count == 0

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_str(self, user):
        """Test the string representation of a post."""
        post = PostFactory(author=user, content='Test post content')
        expected_str = f"Post by {user.username}: {post.content[:30]}"
        assert str(post) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_likes_count(self, user, another_user):
        """Test that the likes_count field is updated correctly."""
        post = PostFactory(author=user)
        
        # Create likes
        PostLikeFactory(user=user, post=post)
        PostLikeFactory(user=another_user, post=post)
        
        assert post.likes_count == 2

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_comments_count(self, user, another_user):
        """Test that the comments_count field is updated correctly."""
        post = PostFactory(author=user)
        
        # Create comments
        CommentFactory(author=user, post=post)
        CommentFactory(author=another_user, post=post)
        
        assert post.comments_count == 2

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_requires_author(self):
        """Test that a post requires an author."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(
                    content='Test post content',
                    code_snippet='print("Hello, world!")'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_requires_content_or_code_snippet(self, user):
        """Test that a post requires either content or code_snippet."""
        # Empty content and code_snippet should fail
        with pytest.raises(ValidationError):
            post = Post(author=user, content='', code_snippet='')
            post.clean()
        
        # With content only should pass
        post = Post(author=user, content='Test content', code_snippet='')
        post.clean()
        
        # With code_snippet only should pass
        post = Post(author=user, content='', code_snippet='print("Hello")')
        post.clean()


class TestCommentModel:
    """Unit tests for the Comment model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_creation(self, user, post):
        """Test creating a comment."""
        comment = Comment.objects.create(
            author=user,
            post=post,
            content='Test comment content'
        )
        
        assert comment.author == user
        assert comment.post == post
        assert comment.content == 'Test comment content'
        assert comment.created_at <= timezone.now()
        assert comment.updated_at <= timezone.now()
        assert comment.likes_count == 0

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_str(self, user, post):
        """Test the string representation of a comment."""
        comment = CommentFactory(author=user, post=post, content='Test comment content')
        expected_str = f"Comment by {user.username} on post {post.id}: {comment.content[:30]}"
        assert str(comment) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_likes_count(self, user, another_user, post):
        """Test that the likes_count field is updated correctly."""
        comment = CommentFactory(author=user, post=post)
        
        # Create likes
        CommentLikeFactory(user=user, comment=comment)
        CommentLikeFactory(user=another_user, comment=comment)
        
        assert comment.likes_count == 2

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_requires_author(self, post):
        """Test that a comment requires an author."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(
                    post=post,
                    content='Test comment content'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_requires_post(self, user):
        """Test that a comment requires a post."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(
                    author=user,
                    content='Test comment content'
                )

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_requires_content(self, user, post):
        """Test that a comment requires content."""
        with pytest.raises(ValidationError):
            comment = Comment(author=user, post=post, content='')
            comment.clean()


class TestPostLikeModel:
    """Unit tests for the PostLike model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_like_creation(self, user, post):
        """Test creating a post like."""
        post_like = PostLike.objects.create(
            user=user,
            post=post
        )
        
        assert post_like.user == user
        assert post_like.post == post
        assert post_like.created_at <= timezone.now()

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_like_str(self, user, post):
        """Test the string representation of a post like."""
        post_like = PostLikeFactory(user=user, post=post)
        expected_str = f"{user.username} likes post {post.id}"
        assert str(post_like) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_post_like_unique_constraint(self, user, post):
        """Test that a user can only like a post once."""
        PostLike.objects.create(user=user, post=post)
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                PostLike.objects.create(user=user, post=post)


class TestCommentLikeModel:
    """Unit tests for the CommentLike model."""

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_like_creation(self, user, comment):
        """Test creating a comment like."""
        comment_like = CommentLike.objects.create(
            user=user,
            comment=comment
        )
        
        assert comment_like.user == user
        assert comment_like.comment == comment
        assert comment_like.created_at <= timezone.now()

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_like_str(self, user, comment):
        """Test the string representation of a comment like."""
        comment_like = CommentLikeFactory(user=user, comment=comment)
        expected_str = f"{user.username} likes comment {comment.id}"
        assert str(comment_like) == expected_str

    @pytest.mark.unit
    @pytest.mark.model
    def test_comment_like_unique_constraint(self, user, comment):
        """Test that a user can only like a comment once."""
        CommentLike.objects.create(user=user, comment=comment)
        
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                CommentLike.objects.create(user=user, comment=comment) 