from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.books.models import Book
from .models import BorrowRequest
from .forms import BorrowRequestForm, BorrowRequestRejectForm
from apps.core.utils import send_notification


class BorrowRequestCreateView(LoginRequiredMixin, View):
    login_url = 'login'
    form_class = BorrowRequestForm
    template_name = 'borrowing/borrow_request_form.html'
    
    def get(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        if not book.is_available_for_borrowing():
            messages.error(request, 'This book is not available for borrowing.')
            return redirect('book_detail', pk=book.pk)

        # already have an active/pending request?
        existing_request = BorrowRequest.objects.filter(
            reader=request.user,
            book=book,
            status__in=['pending', 'approved', 'rejected', 'borrowed']
        ).first()
        if existing_request:
            messages.warning(request, 'You already have a pending or active request for this book.')
            return redirect('book_detail', pk=book.pk)

        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'book': book})

    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        
        if not book.is_available_for_borrowing():
            messages.error(request, 'This book is not available for borrowing.')
            return redirect('book_detail', pk=book.pk)
        
        existing_request = BorrowRequest.objects.filter(
            reader=request.user,
            book=book,
            status__in=['pending', 'approved', 'rejected', 'borrowed']
        ).first()
        if existing_request:
            messages.warning(request, 'You already have a pending or active request for this book.')
            return redirect('book_detail', pk=book.pk)

        form = self.form_class(request.POST)
        if form.is_valid():
            duration = form.cleaned_data.get('duration')
            borrow_request = BorrowRequest.objects.create(
                reader=request.user,
                book=book,
                requested_days=duration
            )
            # Notify the book author (publisher) about the incoming borrow request
            try:
                send_notification(
                    book.author,
                    'borrow_request',
                    f'New borrow request for "{book.title}"',
                    f'{request.user.get_full_name()} requested to borrow your book "{book.title}" for {duration} days.',
                    related_book=book,
                    related_user=request.user
                )
            except Exception:
                # Don't fail the request creation if notification fails
                pass

            messages.success(request, 'Book request submitted! The author will review it shortly.')
            return redirect('book_detail', pk=book.pk)

        # if form invalid render again
        return render(request, self.template_name, {'form': form, 'book': book})


class BorrowRequestApproveView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def post(self, request, pk):
        borrow_request = get_object_or_404(BorrowRequest, pk=pk)
        
        # Check if user is the book author
        if borrow_request.book.author != request.user and not request.user.is_admin_user():
            messages.error(request, 'You are not authorized to approve this request.')
            return redirect('author_books')
        
        borrow_request.approve_request()
        # Notify the reader that their request was approved
        try:
            period = borrow_request.requested_days or None
            due = borrow_request.due_date
            extra = ''
            if period:
                extra = f' You have {period} days (due {due}).'
            else:
                extra = f' Due date: {due}.'
            send_notification(
                borrow_request.reader,
                'borrow_approved',
                f'Borrow request approved for "{borrow_request.book.title}"',
                f'Your request to borrow "{borrow_request.book.title}" was approved by {request.user.get_full_name()}.{extra}',
                related_book=borrow_request.book,
                related_user=request.user
            )
        except Exception:
            pass

        messages.success(request, f'Borrow request from {borrow_request.reader.username} approved!')
        return redirect('author_books')


class BorrowRequestRejectView(LoginRequiredMixin, View):
    template_name = 'borrowing/reject_request.html'
    form_class = BorrowRequestRejectForm
    login_url = 'login'
    
    def get(self, request, pk):
        borrow_request = get_object_or_404(BorrowRequest, pk=pk)
        
        if borrow_request.book.author != request.user and not request.user.is_admin_user():
            messages.error(request, 'You are not authorized to reject this request.')
            return redirect('author_books')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'borrow_request': borrow_request})
    
    def post(self, request, pk):
        borrow_request = get_object_or_404(BorrowRequest, pk=pk)
        
        if borrow_request.book.author != request.user and not request.user.is_admin_user():
            messages.error(request, 'You are not authorized to reject this request.')
            return redirect('author_books')
        
        form = self.form_class(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('reason', 'Request rejected by author')
            borrow_request.reject_request(reason)
            # Notify the reader that their request was rejected
            try:
                send_notification(
                    borrow_request.reader,
                    'borrow_rejected',
                    f'Borrow request rejected for "{borrow_request.book.title}"',
                    f'Your request to borrow "{borrow_request.book.title}" was rejected by {request.user.get_full_name()}. Reason: {reason}',
                    related_book=borrow_request.book,
                    related_user=request.user
                )
            except Exception:
                pass
            messages.success(request, f'Borrow request from {borrow_request.reader.username} rejected!')
            return redirect('author_books')
        
        return render(request, self.template_name, {'form': form, 'borrow_request': borrow_request})


class BorrowRequestReturnView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def post(self, request, pk):
        borrow_request = get_object_or_404(BorrowRequest, pk=pk)
        
        # Check if user is the reader or admin
        if borrow_request.reader != request.user and not request.user.is_admin_user():
            messages.error(request, 'You are not authorized to return this request.')
            return redirect('reader_dashboard')
        
        borrow_request.return_book()
        messages.success(request, f'Book "{borrow_request.book.title}" marked as returned!')
        return redirect('reader_dashboard')


class BorrowRequestCancelView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def post(self, request, pk):
        borrow_request = get_object_or_404(BorrowRequest, pk=pk)
        
        # Check if user is the reader
        if borrow_request.reader != request.user:
            messages.error(request, 'You are not authorized to cancel this request.')
            return redirect('reader_dashboard')
        
        if borrow_request.status != 'pending':
            messages.error(request, 'You can only cancel pending requests.')
            return redirect('reader_dashboard')
        
        borrow_request.cancel_request()
        messages.success(request, 'Borrow request cancelled!')
        return redirect('reader_dashboard')
