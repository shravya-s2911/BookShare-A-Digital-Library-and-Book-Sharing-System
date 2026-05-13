from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:book_id>/', views.BorrowRequestCreateView.as_view(), name='borrow_request_create'),
    path('<int:pk>/approve/', views.BorrowRequestApproveView.as_view(), name='borrow_request_approve'),
    path('<int:pk>/reject/', views.BorrowRequestRejectView.as_view(), name='borrow_request_reject'),
    path('<int:pk>/return/', views.BorrowRequestReturnView.as_view(), name='borrow_request_return'),
    path('<int:pk>/cancel/', views.BorrowRequestCancelView.as_view(), name='borrow_request_cancel'),
]
