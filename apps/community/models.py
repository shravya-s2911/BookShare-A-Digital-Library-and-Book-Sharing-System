from django.db import models
from apps.users.models import User
from apps.books.models import Book


class Community(models.Model):
    """Model for community groups"""
    name = models.CharField(max_length=255, unique=True, help_text='Community name')
    description = models.TextField(help_text='Description of the community')
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_communities'
    )
    members = models.ManyToManyField(
        User,
        related_name='communities',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'
    
    def __str__(self):
        return self.name


class CommunityPost(models.Model):
    """Model for posts in the community hub"""
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='community_posts'
    )
    title = models.CharField(max_length=255, help_text='Post title')
    content = models.TextField(help_text='Post content')
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='community_posts',
        help_text='Associated book (optional)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Community Post'
        verbose_name_plural = 'Community Posts'
        indexes = [
            models.Index(fields=['community', '-created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Comment(models.Model):
    """Model for comments on community posts"""
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(help_text='Comment content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
