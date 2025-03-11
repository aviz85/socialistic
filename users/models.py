from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not username:
            raise ValueError(_('Users must have a username'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for developer social network."""
    
    # Basic info
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=30, unique=True)
    full_name = models.CharField(_('full name'), max_length=100, blank=True)
    bio = models.TextField(_('bio'), blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    # Social profiles
    github_profile = models.URLField(_('GitHub profile'), blank=True)
    stackoverflow_profile = models.URLField(_('StackOverflow profile'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override defaults
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Use custom manager
    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    # Helper methods
    def follow(self, user):
        """Follow another user."""
        if user != self:
            Follow.objects.get_or_create(follower=self, following=user)
    
    def unfollow(self, user):
        """Unfollow another user."""
        Follow.objects.filter(follower=self, following=user).delete()
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.following.count()
    
    class Meta:
        ordering = ['-date_joined']


class Skill(models.Model):
    """Skills that can be associated with users."""
    
    CATEGORY_CHOICES = [
        ('frontend', _('Frontend')),
        ('backend', _('Backend')),
        ('mobile', _('Mobile')),
        ('devops', _('DevOps')),
        ('data', _('Data Science')),
        ('design', _('Design')),
        ('other', _('Other')),
    ]
    
    name = models.CharField(_('name'), max_length=50, unique=True)
    category = models.CharField(_('category'), max_length=20, choices=CATEGORY_CHOICES, default='other')
    users = models.ManyToManyField(User, related_name='skills', blank=True)
    
    def __str__(self):
        return self.name


class ProgrammingLanguage(models.Model):
    """Programming languages used in code snippets."""
    
    name = models.CharField(_('name'), max_length=50, unique=True)
    icon = models.FileField(upload_to='language_icons/', blank=True, null=True)
    
    def __str__(self):
        return self.name


class Follow(models.Model):
    """Represents a follow relationship between users."""
    
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
