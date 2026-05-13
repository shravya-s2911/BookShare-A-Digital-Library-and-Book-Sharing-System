from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('borrow_request', 'Borrow Request'),
        ('borrow_approved', 'Borrow Request Approved'),
        ('borrow_rejected', 'Borrow Request Rejected'),
        ('book_available', 'Book Became Available'),
        ('borrow_due_soon', 'Borrow Due Soon'),
        ('borrow_overdue', 'Borrow Overdue'),
        ('review_added', 'Review Added'),
        ('role_change_approved', 'Role Change Approved'),
        ('role_change_rejected', 'Role Change Rejected'),
        ('book_approved', 'Book Approved'),
        ('book_rejected', 'Book Rejected'),
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES
    )
    
    title = models.CharField(max_length=255)
    
    message = models.TextField()
    
    related_book = models.ForeignKey(
        'books.Book',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notifications'
    )
    
    related_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notifications_from'
    )
    
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
