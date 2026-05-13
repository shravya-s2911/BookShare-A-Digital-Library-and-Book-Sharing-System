from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.books.models import Book
from .models import Review
from .forms import ReviewForm


class ReviewCreateView(LoginRequiredMixin, View):
    template_name = 'reviews/review_form.html'
    form_class = ReviewForm
    login_url = 'login'
    
    def get(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        
        # Check if user already has a review
        existing_review = Review.objects.filter(book=book, reviewer=request.user).first()
        if existing_review:
            messages.warning(request, 'You have already reviewed this book.')
            return redirect('book_detail', pk=book.pk)
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'book': book})
    
    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        form = self.form_class(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Review posted successfully!')
            return redirect('book_detail', pk=book.pk)
        
        return render(request, self.template_name, {'form': form, 'book': book})


class ReviewEditView(LoginRequiredMixin, View):
    template_name = 'reviews/review_form.html'
    form_class = ReviewForm
    login_url = 'login'
    
    def get(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        
        if review.reviewer != request.user:
            messages.error(request, 'You cannot edit this review.')
            return redirect('book_detail', pk=review.book.pk)
        
        form = self.form_class(instance=review)
        return render(request, self.template_name, {'form': form, 'book': review.book, 'review': review})
    
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        
        if review.reviewer != request.user:
            messages.error(request, 'You cannot edit this review.')
            return redirect('book_detail', pk=review.book.pk)
        
        form = self.form_class(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('book_detail', pk=review.book.pk)
        
        return render(request, self.template_name, {'form': form, 'book': review.book, 'review': review})


class ReviewDeleteView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        
        if review.reviewer != request.user:
            messages.error(request, 'You cannot delete this review.')
            return redirect('book_detail', pk=review.book.pk)
        
        book_id = review.book.pk
        review.delete()
        messages.success(request, 'Review deleted successfully!')
        return redirect('book_detail', pk=book_id)
