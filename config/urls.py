"""
URL configuration for Digital Library project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('', include('apps.users.urls')),
    path('books/', include('apps.books.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('borrowing/', include('apps.borrowing.urls')),
    path('community/', include('apps.community.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
