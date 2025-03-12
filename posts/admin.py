from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Post, Comment, PostLike, CommentLike


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'content', 'created_at', 'likes_count')
    readonly_fields = ('created_at', 'likes_count')


class PostLikeInline(admin.TabularInline):
    model = PostLike
    extra = 0
    fields = ('user', 'created_at')
    readonly_fields = ('created_at',)


class CommentLikeInline(admin.TabularInline):
    model = CommentLike
    extra = 0
    fields = ('user', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_author', 'short_content', 'programming_language', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('created_at', 'programming_language')
    search_fields = ('content', 'author__username', 'author__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentInline, PostLikeInline]
    
    def get_author(self, obj):
        return obj.author.username
    get_author.short_description = _('Author')
    get_author.admin_order_field = 'author__username'
    
    def short_content(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    short_content.short_description = _('Content')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'short_content', 'post_link', 'likes_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentLikeInline]
    
    def short_content(self, obj):
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    short_content.short_description = _('Content')
    
    def post_link(self, obj):
        url = f"/admin/posts/post/{obj.post.id}/change/"
        return format_html('<a href="{}">{}</a>', url, f"Post #{obj.post.id}")
    post_link.short_description = _('Post')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post_link', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')
    date_hierarchy = 'created_at'
    
    def post_link(self, obj):
        url = f"/admin/posts/post/{obj.post.id}/change/"
        return format_html('<a href="{}">{}</a>', url, f"Post #{obj.post.id}")
    post_link.short_description = _('Post')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment_link', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'comment__content')
    date_hierarchy = 'created_at'
    
    def comment_link(self, obj):
        url = f"/admin/posts/comment/{obj.comment.id}/change/"
        return format_html('<a href="{}">{}</a>', url, f"Comment #{obj.comment.id}")
    comment_link.short_description = _('Comment')
