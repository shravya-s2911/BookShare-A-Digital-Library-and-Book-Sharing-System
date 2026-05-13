from django.contrib import admin
from .models import BorrowRequest


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ('reader', 'book', 'status', 'requested_at', 'due_date', 'returned_at')
    list_filter = ('status', 'requested_at', 'due_date')
    search_fields = ('reader__username', 'book__title')
    readonly_fields = ('requested_at', 'approved_at', 'returned_at')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('reader', 'book')
        }),
        ('Status', {
            'fields': ('status', 'reason_for_rejection')
        }),
        ('Dates', {
            'fields': ('requested_at', 'approved_at', 'due_date', 'returned_at')
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        approved_count = 0
        for borrow_request in queryset.filter(status='pending'):
            borrow_request.approve_request()
            approved_count += 1
        self.message_user(request, f'{approved_count} request(s) approved.')
    
    def reject_requests(self, request, queryset):
        rejected_count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{rejected_count} request(s) rejected.')
