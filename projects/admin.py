from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Project, ProjectCollaborator, CollaborationRequest


class ProjectCollaboratorInline(admin.TabularInline):
    model = ProjectCollaborator
    extra = 0
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)


class CollaborationRequestInline(admin.TabularInline):
    model = CollaborationRequest
    extra = 0
    fields = ('user', 'message', 'status', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creator', 'status', 'collaborators_count', 'tech_stack_list', 'created_at')
    list_filter = ('status', 'created_at', 'tech_stack')
    search_fields = ('title', 'description', 'creator__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tech_stack',)
    inlines = [ProjectCollaboratorInline, CollaborationRequestInline]
    
    def tech_stack_list(self, obj):
        return ", ".join([skill.name for skill in obj.tech_stack.all()[:5]])
    tech_stack_list.short_description = _('Tech Stack')


@admin.register(ProjectCollaborator)
class ProjectCollaboratorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project_link', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__username', 'project__title')
    date_hierarchy = 'joined_at'
    
    def project_link(self, obj):
        url = f"/admin/projects/project/{obj.project.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.project.title)
    project_link.short_description = _('Project')


@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project_link', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'project__title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_requests', 'reject_requests']
    
    def project_link(self, obj):
        url = f"/admin/projects/project/{obj.project.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.project.title)
    project_link.short_description = _('Project')
    
    def approve_requests(self, request, queryset):
        for collab_request in queryset:
            collab_request.status = 'approved'
            collab_request.save()
            
            # Create collaborator entry if not exists
            ProjectCollaborator.objects.get_or_create(
                project=collab_request.project,
                user=collab_request.user,
                defaults={'role': 'contributor'}
            )
    approve_requests.short_description = _("Approve selected collaboration requests")
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    reject_requests.short_description = _("Reject selected collaboration requests")
