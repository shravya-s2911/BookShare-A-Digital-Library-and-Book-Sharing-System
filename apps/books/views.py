from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
import io
from django.utils import timezone
from apps.users.models import User, RoleChangeRequest
from apps.books.models import Book, BookWishlist, ReadingHistory, BookDownload
from apps.reviews.models import Review
from apps.borrowing.models import BorrowRequest
from .forms import BookForm, BookSearchForm


class BookListView(View):
    template_name = 'books/book_list.html'
    paginate_by = 12
    
    def get(self, request):
        books = Book.objects.filter(status='approved').select_related('author').prefetch_related('reviews')
        
        paginator = Paginator(books, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'books': page_obj.object_list,
        }
        return render(request, self.template_name, context)


class BookSearchView(View):
    template_name = 'books/book_search.html'
    paginate_by = 12
    
    def get(self, request):
        form = BookSearchForm(request.GET)
        books = Book.objects.filter(status='approved').select_related('author')
        
        if request.GET:
            query = request.GET.get('query', '').strip()
            genres = request.GET.getlist('genre')
            availability = request.GET.getlist('availability')
            language = request.GET.get('language', '').strip()
            sort_by = request.GET.get('sort_by', '-created_at')
            
            if query:
                books = books.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(original_author__icontains=query) |
                    Q(author__first_name__icontains=query) |
                    Q(author__last_name__icontains=query)
                )
            
            if genres:
                books = books.filter(genre__in=genres)
            
            if availability:
                books = books.filter(availability__in=availability)
            
            if language:
                books = books.filter(language__icontains=language)
            
            if sort_by:
                books = books.order_by(sort_by)
        
        paginator = Paginator(books, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'form': form,
            'page_obj': page_obj,
            'books': page_obj.object_list,
        }
        return render(request, self.template_name, context)


class BookDetailView(View):
    template_name = 'books/book_detail.html'
    
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk, status='approved')
        reviews = book.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Check if user has already reviewed
        user_review = None
        user_borrow_request = None
        in_wishlist = False
        if request.user.is_authenticated:
            user_review = reviews.filter(reviewer=request.user).first()
            user_borrow_request = BorrowRequest.objects.filter(
                reader=request.user,
                book=book,
                status__in=['pending', 'approved', 'borrowed']
            ).first()
            in_wishlist = BookWishlist.objects.filter(user=request.user, book=book).exists()
        
        context = {
            'book': book,
            'reviews': reviews,
            'avg_rating': avg_rating,
            'user_review': user_review,
            'review_count': reviews.count(),
            'user_borrow_request': user_borrow_request,
            'in_wishlist': in_wishlist,
        }
        return render(request, self.template_name, context)


class BookAddView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/book_form.html'
    form_class = BookForm
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_author() or self.request.user.is_admin_user()
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'action': 'Add'})
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.author = request.user
            book.status = 'pending'
            # Handle uploaded file (store in DB fields)
            upload = request.FILES.get('upload_file') or request.FILES.get('pdf_file')
            if upload:
                try:
                    content = upload.read()
                    book.file_blob = content
                    book.file_name = upload.name
                    book.file_mime = getattr(upload, 'content_type', '')
                except Exception:
                    # ignore file storage problems and continue
                    pass
            book.save()
            messages.success(request, 'Book submitted for approval!')
            return redirect('author_books')
        return render(request, self.template_name, {'form': form, 'action': 'Add'})


class BookEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/book_form.html'
    form_class = BookForm
    login_url = 'login'
    
    def test_func(self):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        return book.author == self.request.user or self.request.user.is_admin_user()
    
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        form = self.form_class(instance=book)
        return render(request, self.template_name, {'form': form, 'book': book, 'action': 'Edit'})
    
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        form = self.form_class(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            if book.status == 'rejected':
                book.status = 'pending'
            # Handle uploaded file (store in DB fields)
            upload = request.FILES.get('upload_file') or request.FILES.get('pdf_file')
            if upload:
                try:
                    content = upload.read()
                    book.file_blob = content
                    book.file_name = upload.name
                    book.file_mime = getattr(upload, 'content_type', '')
                except Exception:
                    pass
            book.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_detail', pk=book.pk)
        return render(request, self.template_name, {'form': form, 'book': book, 'action': 'Edit'})


class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login'
    
    def test_func(self):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        return book.author == self.request.user or self.request.user.is_admin_user()
    
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('author_books')


class BookDownloadView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        
        # Allow download only when the book itself is marked available for download.
        # Borrow-approved users must use the online viewer and are not permitted
        # to retrieve the file directly.
        if not book.is_available_for_download():
            messages.error(request, 'This book is not available for download.')
            return redirect('book_detail', pk=book.pk)

        # Log the download activity
        BookDownload.objects.create(user=request.user, book=book)

        # Serve the file from DB blob if present, otherwise fallback to FileField
        if book.file_blob:
            try:
                bio = io.BytesIO(book.file_blob)
                # FileResponse will stream the BytesIO
                return FileResponse(bio, as_attachment=True, filename=book.file_name or f'{book.pk}.bin')
            except Exception:
                raise Http404("The requested file could not be served from the database.")

        # Fallback to file system stored file
        try:
            return FileResponse(book.pdf_file.open('rb'), as_attachment=True, filename=book.pdf_file.name.split('/')[-1])
        except Exception:
            raise Http404("The requested file was not found on the server.")


class BookViewerView(LoginRequiredMixin, View):
    """Simple endpoint rendering a viewer page for approved borrowings."""

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        today = timezone.now().date()
        allowed = BorrowRequest.objects.filter(
            book=book,
            reader=request.user,
            status__in=['approved', 'borrowed'],
            due_date__gte=today,
            returned_at__isnull=True,
        ).exists()

        if not allowed and book.is_available_for_download():
            allowed = True

        if not allowed:
            return HttpResponseForbidden("You are not allowed to view this file.")

        if not (book.pdf_file or book.file_blob):
            return HttpResponseNotFound("No file available for this book.")

        # pass mime type to template so it can choose correct renderer
        mime = book.file_mime or ''
        return render(request, 'books/book_viewer.html', {'book': book, 'mime': mime})


class BookFileView(LoginRequiredMixin, View):
    """Stream bytes of the book file with access checks."""

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        today = timezone.now().date()
        allowed = BorrowRequest.objects.filter(
            book=book,
            reader=request.user,
            status__in=['approved', 'borrowed'],
            due_date__gte=today,
            returned_at__isnull=True,
        ).exists()

        if not allowed and book.is_available_for_download():
            allowed = True

        if not allowed:
            return HttpResponseForbidden("You are not allowed to access this file.")

        if book.pdf_file:
            f = book.pdf_file
            data = f.read()
            mime = book.file_mime or 'application/pdf'
            filename = f.name.split('/')[-1]
        elif book.file_blob:
            data = book.file_blob
            mime = book.file_mime or 'application/pdf'
            filename = book.file_name or 'book'
        else:
            return HttpResponseNotFound("No file stored for this book.")

        response = HttpResponse(data, content_type=mime)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class WishlistToggleView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        wishlist_entry = BookWishlist.objects.filter(user=request.user, book=book).first()
        
        if wishlist_entry:
            wishlist_entry.delete()
            messages.success(request, 'Removed from wishlist')
        else:
            BookWishlist.objects.create(user=request.user, book=book)
            messages.success(request, 'Added to wishlist')
        
        return redirect('book_detail', pk=book.pk)


class AuthorBooksView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/author_books.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_author() or self.request.user.is_admin_user()
    
    def get(self, request):
        books = Book.objects.filter(author=request.user)
        
        context = {
            'books': books,
            'pending_count': books.filter(status='pending').count(),
            'approved_count': books.filter(status='approved').count(),
            'rejected_count': books.filter(status='rejected').count(),
        }
        return render(request, self.template_name, context)


class AuthorDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/author_dashboard.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_author() or self.request.user.is_admin_user()
    
    def get(self, request):
        # Author-specific data
        books = Book.objects.filter(author=request.user, status='approved')
        borrow_requests = BorrowRequest.objects.filter(book__author=request.user, status='pending')
        recent_downloads = BookDownload.objects.filter(book__author=request.user).select_related('book', 'user')[:10]
        
        # Reader-specific data (they also borrow books)
        user_borrow_requests = BorrowRequest.objects.filter(reader=request.user)
        wishlist = BookWishlist.objects.filter(user=request.user)
        reading_history = ReadingHistory.objects.filter(user=request.user)
        
        context = {
            # Author stats
            'total_books': books.count(),
            'total_requests': borrow_requests.count(),
            'recent_books': books.order_by('-created_at')[:5],
            'pending_borrow_requests': borrow_requests[:5],
            'recent_downloads': recent_downloads,
            
            # Reader stats (they are also readers)
            'active_borrows': user_borrow_requests.filter(status__in=['approved', 'borrowed']),
            'pending_requests': user_borrow_requests.filter(status='pending'),
            'wishlist': wishlist,
            'reading_history': reading_history,
        }
        return render(request, self.template_name, context)


class ReaderDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/reader_dashboard.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_reader()
    
    def get(self, request):
        borrow_requests = BorrowRequest.objects.filter(reader=request.user)
        wishlist = BookWishlist.objects.filter(user=request.user)
        reading_history = ReadingHistory.objects.filter(user=request.user)
        
        context = {
            'active_borrows': borrow_requests.filter(status__in=['approved', 'borrowed']),
            'pending_requests': borrow_requests.filter(status='pending'),
            'wishlist': wishlist,
            'reading_history': reading_history,
        }
        return render(request, self.template_name, context)


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/admin_dashboard.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get(self, request):
        # Admin monitor stats
        total_users = User.objects.count()
        total_books = Book.objects.count()
        pending_book_requests = Book.objects.filter(status='pending').count()
        pending_role_requests = RoleChangeRequest.objects.filter(status='pending').count()
        recent_books = Book.objects.order_by('-created_at')[:5]
        recent_users = User.objects.order_by('-created_at')[:5]

        # Author-like data (for admin-author combined tab)
        borrow_requests = BorrowRequest.objects.filter(status='pending')
        recent_downloads = BookDownload.objects.select_related('book', 'user').order_by('-downloaded_at')[:10]
        user_borrow_requests = BorrowRequest.objects.filter(reader=request.user)
        wishlist = BookWishlist.objects.filter(user=request.user)
        reading_history = ReadingHistory.objects.filter(user=request.user)

        context = {
            # Monitor stats
            'total_users': total_users,
            'total_books': total_books,
            'pending_book_requests': pending_book_requests,
            'pending_role_requests': pending_role_requests,
            'recent_books': recent_books,
            'recent_users': recent_users,

            # Author-like context (used by the Author tab in the admin dashboard)
            'total_requests': borrow_requests.count(),
            'recent_downloads': recent_downloads,
            'pending_borrow_requests': borrow_requests[:5],
            'user_borrow_requests': user_borrow_requests,
            'active_borrows': user_borrow_requests.filter(status__in=['approved', 'borrowed']),
            'pending_requests': user_borrow_requests.filter(status='pending'),
            'wishlist': wishlist,
            'reading_history': reading_history,
            'recent_books': recent_books,
        }
        return render(request, self.template_name, context)


class AdminBookRequestsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/admin_book_requests.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get(self, request):
        books = Book.objects.filter(status='pending')
        context = {
            'books': books,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        book_id = request.POST.get('book_id')
        action = request.POST.get('action')
        book = get_object_or_404(Book, pk=book_id)
        
        if action == 'approve':
            book.status = 'approved'
            message = f'Book "{book.title}" approved!'
        elif action == 'reject':
            book.status = 'rejected'
            book.rejection_reason = request.POST.get('reason', '')
            message = f'Book "{book.title}" rejected!'
        else:
            message = 'Invalid action'
        
        book.save()
        messages.success(request, message)
        return redirect('admin_book_requests')


class AdminUsersView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/admin_users.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get(self, request):
        users = User.objects.all()
        context = {
            'users': users,
            'total_users': users.count(),
            'readers': users.filter(role='reader').count(),
            'authors': users.filter(role='author').count(),
        }
        return render(request, self.template_name, context)


class AdminRoleRequestsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'books/admin_role_requests.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get(self, request):
        role_requests = RoleChangeRequest.objects.filter(status='pending')
        context = {
            'role_requests': role_requests,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        role_request = get_object_or_404(RoleChangeRequest, pk=request_id)
        
        if action == 'approve':
            role_request.user.role = role_request.requested_role
            role_request.user.save()
            role_request.status = 'approved'
            message = f'Role change request for {role_request.user.username} approved!'
        elif action == 'reject':
            role_request.status = 'rejected'
            role_request.admin_comment = request.POST.get('reason', '')
            message = f'Role change request for {role_request.user.username} rejected!'
        else:
            message = 'Invalid action'
        
        role_request.save()
        messages.success(request, message)
        return redirect('admin_role_requests')
