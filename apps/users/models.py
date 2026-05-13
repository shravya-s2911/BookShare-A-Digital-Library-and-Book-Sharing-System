from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('author', 'Author'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='reader',
        help_text='User role in the system'
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        help_text='User biography or description'
    )
    
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    
    favorite_genres = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Comma-separated list of favorite genres for readers'
    )
    
    is_approved = models.BooleanField(
        default=True,
        help_text='Whether the user account is approved'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def is_reader(self):
        return self.role == 'reader'
    
    def is_author(self):
        return self.role == 'author'
    
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    def get_role_display_custom(self):
        return self.get_role_display()


class RoleChangeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='role_change_request'
    )
    
    requested_role = models.CharField(
        max_length=10,
        choices=User.ROLE_CHOICES
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for role change request'
    )
    
    admin_comment = models.TextField(
        blank=True,
        null=True,
        help_text='Admin comment on the request (e.g., reason for rejection)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Role Change Request'
        verbose_name_plural = 'Role Change Requests'
    
    def __str__(self):
        return f"{self.user.username} - {self.requested_role} ({self.status})"
