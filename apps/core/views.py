from django.views.generic import TemplateView
from apps.books.models import Book
from django.db.models import Avg


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured books (approved books with highest ratings)
        featured_books = Book.objects.filter(status='approved').annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:4]
        
        context['featured_books'] = featured_books
        return context
