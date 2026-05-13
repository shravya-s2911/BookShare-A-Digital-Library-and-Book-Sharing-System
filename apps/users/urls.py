from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('role-change-request/', views.RoleChangeRequestView.as_view(), name='role_change_request'),
]
