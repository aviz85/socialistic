from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from users.models import Skill


class Project(models.Model):
    """A project that users can collaborate on."""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
    ]
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='created_projects',
        on_delete=models.CASCADE
    )
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'))
    repo_url = models.URLField(_('repository URL'), blank=True)
    tech_stack = models.ManyToManyField(Skill, related_name='projects')
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectCollaborator',
        related_name='collaborated_projects'
    )
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def collaborators_count(self):
        return self.collaborators.count()
    
    def clean(self):
        """Validate the project."""
        if not self.title:
            raise ValidationError("Project title is required.")
        
        if self.repo_url and not self.repo_url.startswith(('http://', 'https://')):
            raise ValidationError("Repository URL must be a valid URL.")
        
        super().clean()
    
    def save(self, *args, **kwargs):
        """Save the project and add the creator as a collaborator."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Add creator as owner collaborator if this is a new project
        if is_new:
            from projects.models import ProjectCollaborator
            ProjectCollaborator.objects.create(
                user=self.creator,
                project=self,
                role='owner'
            )
    
    class Meta:
        ordering = ['-created_at']


class ProjectCollaborator(models.Model):
    """Represents a collaboration relationship between a user and a project."""
    
    ROLE_CHOICES = [
        ('owner', _('Owner')),
        ('contributor', _('Contributor')),
        ('viewer', _('Viewer')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='contributor')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'project')
        
    def __str__(self):
        return f"{self.user.username} on {self.project.title}"


class CollaborationRequest(models.Model):
    """A request to collaborate on a project."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='collaboration_requests',
        on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        Project,
        related_name='collaboration_requests',
        on_delete=models.CASCADE
    )
    message = models.TextField(_('message'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'project')
        
    def __str__(self):
        return f"{self.user.username} requests to join {self.project.title} ({self.status})"
        
    def clean(self):
        """Validate the collaboration request."""
        # Check if user is the project creator
        if self.user == self.project.creator:
            raise ValidationError("You cannot request to collaborate on your own project.")
        
        # Check if user is already a collaborator
        if self.project.collaborators.filter(id=self.user.id).exists():
            raise ValidationError("You are already a collaborator on this project.")
        
        super().clean()
    
    def accept(self):
        """Accept the collaboration request."""
        # Add user as a collaborator
        ProjectCollaborator.objects.create(
            project=self.project,
            user=self.user,
            role='contributor'
        )
        
        # Update request status
        self.status = 'approved'
        self.save()
        
        return True
    
    def reject(self):
        """Reject the collaboration request."""
        self.status = 'rejected'
        self.save()
        
        return True
