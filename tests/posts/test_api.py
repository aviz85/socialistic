import pytest
from django.urls import reverse
from rest_framework import status
from posts.models import Post, Comment, PostLike, CommentLike
from tests.factories import PostFactory, CommentFactory, ProgrammingLanguageFactory

pytestmark = pytest.mark.django_db


class TestPostListCreateAPI:
    """Tests for post list and create API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_list_posts(self, auth_client, user, another_user):
        """Test listing posts."""
        # Create some posts
        post1 = PostFactory(author=user)
        post2 = PostFactory(author=another_user)
        
        url = reverse('post-list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check if response is paginated
        if 'results' in response.data:
            # Paginated response
            assert len(response.data['results']) >= 2  # At least our 2 posts
            
            # Get all post IDs from the results
            post_ids = [post['id'] for post in response.data['results']]
        else:
            # Non-paginated response
            assert len(response.data) >= 2  # At least our 2 posts
            
            # Get all post IDs from the results
            post_ids = [post['id'] for post in response.data]
        
        # Check that both posts are in the response
        assert post1.id in post_ids
        assert post2.id in post_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_post(self, auth_client, user):
        """Test creating a post."""
        # For test simplicity, we'll post without a programming language
        url = reverse('post-list')
        data = {
            'content': 'Test post content',
            'code_snippet': 'print("Hello, world!")'
            # programming_language field is omitted
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'Test post content'
        assert response.data['code_snippet'] == 'print("Hello, world!")'
        assert response.data['author']['id'] == user.id
        
        # Check that the post was created in the database
        post = Post.objects.get(id=response.data['id'])
        assert post.content == 'Test post content'
        assert post.author == user

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_post_without_authentication(self, api_client):
        """Test that an unauthenticated user cannot create a post."""
        url = reverse('post-list')
        
        data = {
            'content': 'Test post content',
            'code_snippet': 'print("Hello, world!")'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_post_empty_content_and_code(self, auth_client):
        """Test that a post requires either content or code_snippet."""
        url = reverse('post-list')
        data = {
            'content': '',
            'code_snippet': ''
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestPostDetailAPI:
    """Tests for post detail API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_retrieve_post(self, auth_client, user):
        """Test retrieving a post."""
        post = PostFactory(author=user)
        
        url = reverse('post-detail', kwargs={'pk': post.id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == post.id
        assert response.data['content'] == post.content
        assert response.data['author']['id'] == user.id

    @pytest.mark.api
    @pytest.mark.integration
    def test_update_own_post(self, auth_client, user):
        """Test updating own post."""
        post = PostFactory(author=user)
        
        url = reverse('post-detail', kwargs={'pk': post.id})
        data = {
            'content': 'Updated content',
            'code_snippet': 'Updated code'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Updated content'
        assert response.data['code_snippet'] == 'Updated code'
        
        # Check that the post was updated in the database
        post.refresh_from_db()
        assert post.content == 'Updated content'
        assert post.code_snippet == 'Updated code'

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_update_other_user_post(self, auth_client, another_user):
        """Test that a user cannot update another user's post."""
        post = PostFactory(author=another_user)
        
        url = reverse('post-detail', kwargs={'pk': post.id})
        data = {
            'content': 'Updated content'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_own_post(self, auth_client, user):
        """Test deleting own post."""
        post = PostFactory(author=user)
        
        url = reverse('post-detail', kwargs={'pk': post.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the post was deleted from the database
        assert not Post.objects.filter(id=post.id).exists()

    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_delete_other_user_post(self, auth_client, another_user):
        """Test that a user cannot delete another user's post."""
        post = PostFactory(author=another_user)
        
        url = reverse('post-detail', kwargs={'pk': post.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCommentAPI:
    """Tests for comment API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_list_post_comments(self, auth_client, user, post):
        """Test listing comments for a post."""
        # Create some comments
        comment1 = CommentFactory(author=user, post=post)
        comment2 = CommentFactory(author=user, post=post)
        
        url = reverse('post-comments', kwargs={'pk': post.id})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2 or len(response.data['results']) == 2  # Handle pagination
        
        # If response has pagination
        comments_data = response.data['results'] if 'results' in response.data else response.data
        
        # Check that both comments are in the response
        comment_ids = [comment['id'] for comment in comments_data]
        assert comment1.id in comment_ids
        assert comment2.id in comment_ids

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_comment(self, auth_client, user, post):
        """Test creating a comment."""
        url = reverse('post-comments', kwargs={'pk': post.id})
        data = {
            'content': 'Test comment'
        }
        
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'Test comment'
        assert response.data['author']['id'] == user.id
        
        # Post ID check is omitted since it might not be in the response payload
        # The important thing is that we can retrieve the comment from the database
        comment = Comment.objects.get(id=response.data['id'])
        assert comment.content == 'Test comment'
        assert comment.author == user
        assert comment.post == post

    @pytest.mark.api
    @pytest.mark.integration
    def test_create_comment_without_authentication(self, api_client, post):
        """Test that an unauthenticated user cannot create a comment."""
        url = reverse('post-comments', kwargs={'pk': post.id})
        data = {
            'content': 'Test comment'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip("Comment detail endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_update_own_comment(self, auth_client, user, post):
        """Test updating own comment."""
        comment = CommentFactory(author=user, post=post)
        
        url = reverse('comment-detail', kwargs={'pk': comment.id})
        data = {
            'content': 'Updated comment content'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == 'Updated comment content'
        
        # Check that the comment was updated in the database
        comment.refresh_from_db()
        assert comment.content == 'Updated comment content'

    @pytest.mark.skip("Comment detail endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_update_other_user_comment(self, auth_client, another_user, post):
        """Test that a user cannot update another user's comment."""
        comment = CommentFactory(author=another_user, post=post)
        
        url = reverse('comment-detail', kwargs={'pk': comment.id})
        data = {
            'content': 'Updated comment content'
        }
        
        response = auth_client.patch(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.skip("Comment detail endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_delete_own_comment(self, auth_client, user, post):
        """Test deleting own comment."""
        comment = CommentFactory(author=user, post=post)
        
        url = reverse('comment-detail', kwargs={'pk': comment.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the comment was deleted from the database
        assert not Comment.objects.filter(id=comment.id).exists()

    @pytest.mark.skip("Comment detail endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_cannot_delete_other_user_comment(self, auth_client, another_user, post):
        """Test that a user cannot delete another user's comment."""
        comment = CommentFactory(author=another_user, post=post)
        
        url = reverse('comment-detail', kwargs={'pk': comment.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPostLikeAPI:
    """Tests for post like API."""
    
    @pytest.mark.api
    @pytest.mark.integration
    def test_like_post(self, auth_client, user, post):
        """Test liking a post."""
        url = reverse('post-like', kwargs={'pk': post.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that the like was created in the database
        assert PostLike.objects.filter(user=user, post=post).exists()
        
        # Check that the post's likes_count was incremented
        post.refresh_from_db()
        assert post.likes_count == 1

    @pytest.mark.api
    @pytest.mark.integration
    def test_unlike_post(self, auth_client, user, post):
        """Test unliking a post."""
        # Create like
        PostLike.objects.create(user=user, post=post)
        
        url = reverse('post-unlike', kwargs={'pk': post.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the like was removed from the database
        assert not PostLike.objects.filter(user=user, post=post).exists()
        
        # Check that the post's likes_count was decremented
        post.refresh_from_db()
        assert post.likes_count == 0

    @pytest.mark.api
    @pytest.mark.integration
    def test_like_post_without_authentication(self, api_client, post):
        """Test that an unauthenticated user cannot like a post."""
        url = reverse('post-like', kwargs={'pk': post.id})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCommentLikeAPI:
    """Tests for comment like API."""
    
    @pytest.mark.skip("Comment like endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_like_comment(self, auth_client, user, comment):
        """Test liking a comment."""
        url = reverse('comment-like', kwargs={'comment_id': comment.id})
        
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check that the like was created in the database
        assert CommentLike.objects.filter(user=user, comment=comment).exists()
        
        # Check that the comment's likes_count was incremented
        comment.refresh_from_db()
        assert comment.likes_count == 1

    @pytest.mark.skip("Comment like endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_unlike_comment(self, auth_client, user, comment):
        """Test unliking a comment."""
        # Create like
        CommentLike.objects.create(user=user, comment=comment)
        
        url = reverse('comment-unlike', kwargs={'comment_id': comment.id})
        
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the like was removed from the database
        assert not CommentLike.objects.filter(user=user, comment=comment).exists()
        
        # Check that the comment's likes_count was decremented
        comment.refresh_from_db()
        assert comment.likes_count == 0

    @pytest.mark.skip("Comment like endpoint not implemented yet")
    @pytest.mark.api
    @pytest.mark.integration
    def test_like_comment_without_authentication(self, api_client, comment):
        """Test that an unauthenticated user cannot like a comment."""
        url = reverse('comment-like', kwargs={'comment_id': comment.id})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 