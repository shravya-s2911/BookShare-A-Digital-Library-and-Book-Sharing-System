from django.contrib import admin
from .models import Book, BookWishlist, ReadingHistory


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'status', 'availability', 'created_at')
    list_filter = ('status', 'genre', 'availability', 'created_at')
    search_fields = ('title', 'author__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'description', 'genre', 'language')
        }),
        ('Publication Details', {
            'fields': ('publisher', 'isbn', 'pages', 'publication_date')
        }),
        ('Media', {
            'fields': ('cover_image', 'pdf_file')
        }),
        ('Availability', {
            'fields': ('availability', 'status', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_books', 'reject_books']
    
    def approve_books(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{updated} book(s) approved.')
    
    def reject_books(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{len(queryset)} book(s) rejected.')


@admin.register(BookWishlist)
class BookWishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('added_at',)


@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'completed', 'added_at', 'completed_at')
    list_filter = ('completed', 'added_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('added_at',)
