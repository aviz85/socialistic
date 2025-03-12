from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Skill, ProgrammingLanguage, Follow


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'full_name', 'is_staff', 'date_joined', 'followers_count', 'following_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('full_name', 'bio', 'profile_image')}),
        (_('Social Profiles'), {'fields': ('github_profile', 'stackoverflow_profile')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions', 'skills')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'users_count')
    list_filter = ('category',)
    search_fields = ('name',)
    
    def users_count(self, obj):
        return obj.users.count()
    users_count.short_description = _('Users')


class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'posts_count')
    search_fields = ('name',)
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = _('Posts')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(ProgrammingLanguage, ProgrammingLanguageAdmin)
admin.site.register(Follow, FollowAdmin)
