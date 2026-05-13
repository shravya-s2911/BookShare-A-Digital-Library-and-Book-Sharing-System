from django.db import models
from apps.users.models import User


class Book(models.Model):
    GENRE_CHOICES = (
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('thriller', 'Thriller'),
        ('horror', 'Horror'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('self-help', 'Self-Help'),
        ('poetry', 'Poetry'),
        ('children', 'Children'),
        ('young-adult', 'Young Adult'),
        ('educational', 'Educational'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    AVAILABILITY_CHOICES = (
        ('borrow', 'Available for Borrowing'),
        ('download', 'Available for Download'),
        ('both', 'Both Borrowing and Download'),
        ('unavailable', 'Currently Unavailable'),
    )
    
    title = models.CharField(
        max_length=255,
        help_text='Book title'
    )
    
    original_author = models.CharField(
        max_length=255,
        default='Unknown',
        help_text='Original author who wrote the book'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_books',
        limit_choices_to={'role__in': ['author', 'admin']}
    )
    
    description = models.TextField(
        help_text='Detailed description of the book'
    )
    
    genre = models.CharField(
        max_length=50,
        choices=GENRE_CHOICES,
        help_text='Genre of the book'
    )
    
    language = models.CharField(
        max_length=50,
        default='English',
        help_text='Language of the book'
    )
    
    publication_date = models.DateField(
        help_text='Date of publication'
    )
    
    publisher = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Publisher of the book'
    )
    
    isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text='ISBN number'
    )
    
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True,
        help_text='Book cover image'
    )
    
    pdf_file = models.FileField(
        upload_to='book_files/',
        blank=True,
        null=True,
        verbose_name='PDF/EPUB file',
        help_text='PDF/EPUB file of the book (for download)'
    )

    # Store uploaded file bytes in the database (optional/alternative to FileField)
    file_blob = models.BinaryField(
        blank=True,
        null=True,
        help_text='Binary content of uploaded book file (pdf/epub)'
    )

    file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Original filename of uploaded book file'
    )

    file_mime = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='MIME type of the uploaded file'
    )
    
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='borrow',
        help_text='How the book is available'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Publication status of the book'
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for rejection (if rejected)'
    )
    
    pages = models.IntegerField(
        blank=True,
        null=True,
        help_text='Number of pages'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['genre']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.get_full_name()}"
    
    def is_available_for_borrowing(self):
        return self.status == 'approved' and self.availability in ['borrow', 'both']
    
    def is_available_for_download(self):
        # Available for download if approved and availability allows it, and either a stored file or file field exists
        has_file = bool(self.file_blob) or bool(self.pdf_file)
        return self.status == 'approved' and self.availability in ['download', 'both'] and has_file
    
    def is_published(self):
        return self.status == 'approved'


class BookWishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='wishlist_entries'
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-added_at']
        verbose_name = 'Book Wishlist'
        verbose_name_plural = 'Book Wishlists'
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class ReadingHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reading_history'
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='read_by'
    )
    
    completed = models.BooleanField(
        default=False,
        help_text='Whether the user has completed reading the book'
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the user completed reading the book'
    )
    
    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-added_at']
        verbose_name = 'Reading History'
        verbose_name_plural = 'Reading Histories'
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class BookDownload(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='downloads'
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='downloads'
    )
    
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = 'Book Download'
        verbose_name_plural = 'Book Downloads'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['book']),
        ]
        
    def __str__(self):
        return f"{self.user.username} downloaded {self.book.title}"
