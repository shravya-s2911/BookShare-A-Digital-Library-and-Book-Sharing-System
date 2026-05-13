from django.db import models
from apps.users.models import User
from apps.books.models import Book


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text='Rating from 1 to 5 stars'
    )
    
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Review title'
    )
    
    content = models.TextField(
        help_text='Your review content'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('book', 'reviewer')
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [
            models.Index(fields=['book']),
            models.Index(fields=['reviewer']),
        ]
    
    def __str__(self):
        return f"{self.reviewer.username} - {self.book.title} ({self.rating}*)"
