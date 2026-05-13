from django.urls import path
from . import views

urlpatterns = [
    # Community Hub main page
    path('', views.CommunityHubView.as_view(), name='community_hub'),
    
    # Community management
    path('create/', views.CreateCommunityView.as_view(), name='create_community'),
    path('<int:pk>/', views.CommunityDetailView.as_view(), name='community_detail'),
    
    # Post management
    path('community/<int:community_pk>/post/create/', views.CreatePostView.as_view(), name='create_post'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/edit/', views.EditPostView.as_view(), name='edit_post'),
    path('post/<int:pk>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    
    # Comment management
    path('comment-history/', views.CommentHistoryView.as_view(), name='comment_history'),
    path('comment/<int:pk>/edit/', views.EditCommentView.as_view(), name='edit_comment'),
    path('comment/<int:pk>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),
]
