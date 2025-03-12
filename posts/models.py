from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import ProgrammingLanguage
from django.core.exceptions import ValidationError


class Post(models.Model):
    """A post in the developer social network."""
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField(_('content'))
    code_snippet = models.TextField(_('code snippet'), blank=True, null=True)
    programming_language = models.ForeignKey(
        ProgrammingLanguage, 
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='PostLike',
        related_name='liked_posts'
    )
    
    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:30]}"
    
    def clean(self):
        """Validate that a post has either content or code_snippet."""
        if not self.content and not self.code_snippet:
            raise ValidationError(_('A post must have either content or code snippet.'))
        super().clean()
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    """A comment on a post."""
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CommentLike',
        related_name='liked_comments'
    )
    
    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}: {self.content[:30]}"
    
    def clean(self):
        """Validate that a comment has content."""
        if not self.content:
            raise ValidationError(_('A comment must have content.'))
        super().clean()
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    class Meta:
        ordering = ['created_at']


class PostLike(models.Model):
    """A like on a post."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        
    def __str__(self):
        return f"{self.user.username} likes post {self.post.id}"


class CommentLike(models.Model):
    """A like on a comment."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
        
    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"
