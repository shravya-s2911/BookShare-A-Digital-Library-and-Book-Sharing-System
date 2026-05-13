from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('search/', views.BookSearchView.as_view(), name='book_search'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('add/', views.BookAddView.as_view(), name='book_add'),
    path('<int:pk>/edit/', views.BookEditView.as_view(), name='book_edit'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    path('<int:pk>/download/', views.BookDownloadView.as_view(), name='book_download'),
    # viewer & file streaming for borrowed books
    path('<int:pk>/view/', views.BookViewerView.as_view(), name='book_viewer'),
    path('<int:pk>/file/', views.BookFileView.as_view(), name='book_file'),
    path('<int:pk>/wishlist-toggle/', views.WishlistToggleView.as_view(), name='wishlist_toggle'),
    path('author/books/', views.AuthorBooksView.as_view(), name='author_books'),
    path('author/dashboard/', views.AuthorDashboardView.as_view(), name='author_dashboard'),
    path('reader/dashboard/', views.ReaderDashboardView.as_view(), name='reader_dashboard'),
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/book-requests/', views.AdminBookRequestsView.as_view(), name='admin_book_requests'),
    path('admin/users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin/role-requests/', views.AdminRoleRequestsView.as_view(), name='admin_role_requests'),
]
