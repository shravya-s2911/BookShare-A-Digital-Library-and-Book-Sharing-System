from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:book_id>/', views.ReviewCreateView.as_view(), name='review_add'),
    path('<int:pk>/edit/', views.ReviewEditView.as_view(), name='review_edit'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
]
