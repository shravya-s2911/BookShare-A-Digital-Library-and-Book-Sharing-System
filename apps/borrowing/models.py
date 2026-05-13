from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.books.models import Book


class BorrowRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('borrowed', 'Borrowed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    reader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrow_requests'
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrow_requests'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the request was approved'
    )
    
    # the reader selects a preferred number of days when making the request
    DURATION_CHOICES = [
        (7, '7 days'),
        (10, '10 days'),
        (14, '14 days'),
        (21, '21 days'),
    ]
    requested_days = models.PositiveIntegerField(
        choices=DURATION_CHOICES,
        blank=True,
        null=True,
        help_text='Number of days reader would like to borrow the book'
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        help_text='When the book should be returned'
    )
    
    returned_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the book was returned'
    )
    
    reason_for_rejection = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for rejecting the request'
    )
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Borrow Request'
        verbose_name_plural = 'Borrow Requests'
        indexes = [
            models.Index(fields=['reader']),
            models.Index(fields=['book']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.reader.username} - {self.book.title} ({self.status})"
    
    def is_overdue(self):
        if self.due_date and self.status in ['approved', 'borrowed'] and not self.returned_at:
            return timezone.now().date() > self.due_date
        return False
    
    def days_remaining(self):
        if self.due_date and self.status in ['approved', 'borrowed'] and not self.returned_at:
            return (self.due_date - timezone.now().date()).days
        return None
    
    def approve_request(self):
        from django.conf import settings
        self.status = 'approved'
        self.approved_at = timezone.now()
        # if the reader picked a specific duration, use it; otherwise fall back to global default
        days = self.requested_days or settings.BOOK_BORROW_DAYS
        self.due_date = timezone.now().date() + timedelta(days=days)
        self.save()
    
    def reject_request(self, reason):
        self.status = 'rejected'
        self.reason_for_rejection = reason
        self.save()
    
    def cancel_request(self):
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save()
    
    def return_book(self):
        self.returned_at = timezone.now()
        self.save()
