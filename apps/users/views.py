from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User, RoleChangeRequest
from .forms import CustomUserCreationForm, CustomUserChangeForm, RoleChangeRequestForm


class RegisterView(View):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'users/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_approved:
                messages.error(request, 'Your account is not yet approved by admin.')
                return render(request, self.template_name)
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'
    login_url = 'login'
    
    def get(self, request):
        context = {
            'user': request.user,
        }
        return render(request, self.template_name, context)


class ProfileEditView(LoginRequiredMixin, View):
    template_name = 'users/profile_edit.html'
    form_class = CustomUserChangeForm
    login_url = 'login'
    
    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


class PasswordChangeView(LoginRequiredMixin, BasePasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('profile')
    login_url = 'login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def get(self, request):
        user = request.user
        
        if user.is_admin_user():
            return redirect('admin_dashboard')
        elif user.is_author():
            return redirect('author_dashboard')
        else:
            return redirect('reader_dashboard')


class RoleChangeRequestView(LoginRequiredMixin, View):
    template_name = 'users/role_change_request.html'
    form_class = RoleChangeRequestForm
    login_url = 'login'
    
    def get(self, request):
        # Check if user already has a pending request
        pending_request = RoleChangeRequest.objects.filter(
            user=request.user,
            status='pending'
        ).first()
        
        if pending_request:
            messages.info(request, 'You already have a pending role change request.')
            return redirect('profile')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Delete any previous requests
            RoleChangeRequest.objects.filter(user=request.user).delete()
            
            role_change = form.save(commit=False)
            role_change.user = request.user
            role_change.save()
            
            messages.success(request, 'Role change request submitted. Admin will review it shortly.')
            return redirect('profile')
        return render(request, self.template_name, {'form': form})
