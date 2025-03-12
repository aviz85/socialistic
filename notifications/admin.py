from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html

from .models import Notification, NotificationSetting


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'type', 'short_text', 'is_read', 'content_type', 'object_link', 'created_at')
    list_filter = ('type', 'is_read', 'created_at', 'content_type')
    search_fields = ('recipient__username', 'sender__username', 'text')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']
    
    def short_text(self, obj):
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text
    short_text.short_description = _('Text')
    
    def object_link(self, obj):
        if obj.content_type and obj.object_id:
            content_type = obj.content_type.model
            try:
                model_class = obj.content_type.model_class()
                object_instance = model_class.objects.get(pk=obj.object_id)
                
                # Generate appropriate admin URL based on content type
                if content_type == 'post':
                    url = f"/admin/posts/post/{obj.object_id}/change/"
                    return format_html('<a href="{}">{}</a>', url, f"Post #{obj.object_id}")
                elif content_type == 'comment':
                    url = f"/admin/posts/comment/{obj.object_id}/change/"
                    return format_html('<a href="{}">{}</a>', url, f"Comment #{obj.object_id}")
                elif content_type == 'follow':
                    url = f"/admin/users/follow/{obj.object_id}/change/"
                    return format_html('<a href="{}">{}</a>', url, f"Follow #{obj.object_id}")
                elif content_type == 'project':
                    url = f"/admin/projects/project/{obj.object_id}/change/"
                    return format_html('<a href="{}">{}</a>', url, f"Project #{obj.object_id}")
                elif content_type == 'collaborationrequest':
                    url = f"/admin/projects/collaborationrequest/{obj.object_id}/change/"
                    return format_html('<a href="{}">{}</a>', url, f"Request #{obj.object_id}")
                else:
                    return f"{content_type} #{obj.object_id}"
            except Exception:
                return f"{content_type} #{obj.object_id} (not found)"
        return "-"
    object_link.short_description = _('Related Object')
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = _("Mark selected notifications as read")
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = _("Mark selected notifications as unread")


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_summary', 'push_summary')
    search_fields = ('user__username', 'user__email')
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Email Notifications'), {
            'fields': ('email_likes', 'email_comments', 'email_follows', 'email_mentions',
                      'email_project_invites', 'email_project_requests'),
        }),
        (_('Push Notifications'), {
            'fields': ('push_likes', 'push_comments', 'push_follows', 'push_mentions',
                      'push_project_invites', 'push_project_requests'),
        }),
    )
    
    def email_summary(self, obj):
        enabled = []
        if obj.email_likes: enabled.append('Likes')
        if obj.email_comments: enabled.append('Comments')
        if obj.email_follows: enabled.append('Follows')
        if obj.email_mentions: enabled.append('Mentions')
        if obj.email_project_invites: enabled.append('Project invites')
        if obj.email_project_requests: enabled.append('Project requests')
        
        if enabled:
            return ", ".join(enabled)
        return "None"
    email_summary.short_description = _('Email Notifications')
    
    def push_summary(self, obj):
        enabled = []
        if obj.push_likes: enabled.append('Likes')
        if obj.push_comments: enabled.append('Comments')
        if obj.push_follows: enabled.append('Follows')
        if obj.push_mentions: enabled.append('Mentions')
        if obj.push_project_invites: enabled.append('Project invites')
        if obj.push_project_requests: enabled.append('Project requests')
        
        if enabled:
            return ", ".join(enabled)
        return "None"
    push_summary.short_description = _('Push Notifications')
