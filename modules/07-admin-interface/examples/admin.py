# blog/admin.py — Module 07 example
from django.contrib import admin
from django.utils import timezone
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ['author', 'body', 'is_approved']
    readonly_fields = ['author', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'comment_count']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'body', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    ordering = ['-published_at']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommentInline]

    fieldsets = (
        ('Content', {'fields': ('title', 'slug', 'author', 'body')}),
        ('Categorisation', {'fields': ('category', 'tags')}),
        ('Publishing', {'fields': ('status', 'published_at'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Comments')
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.action(description='Publish selected posts')
    def publish_posts(self, request, queryset):
        count = queryset.filter(status='draft').update(
            status='published',
            published_at=timezone.now(),
        )
        self.message_user(request, f'{count} post(s) published.')

    actions = [publish_posts]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['body', 'author__username', 'post__title']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    actions = [approve_comments]
