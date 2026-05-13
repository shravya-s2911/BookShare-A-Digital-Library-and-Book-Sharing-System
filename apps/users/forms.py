from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
import re
from .models import User, RoleChangeRequest


class CustomUserCreationForm(UserCreationForm):
    REGISTRATION_ROLE_CHOICES = (
        ('reader', 'Reader - Browse and borrow books'),
        ('author', 'Author - Publish and share books'),
    )
    
    role = forms.ChoiceField(
        choices=REGISTRATION_ROLE_CHOICES,
        initial='reader',
        widget=forms.RadioSelect(),
        help_text='Choose your role in the system'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Your first name'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Your last name'
    )
    
    email = forms.EmailField(
        required=True,
        help_text='A valid email address'
    )
    
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Tell us about yourself'
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'role', 'bio', 'password1', 'password2')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Passwords do not match.')
            
            # Check password length
            if len(password1) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            
            # Check for at least one uppercase letter
            if not re.search(r'[A-Z]', password1):
                raise ValidationError('Password must contain at least one uppercase letter (A-Z).')
            
            # Check for at least one number
            if not re.search(r'[0-9]', password1):
                raise ValidationError('Password must contain at least one number (0-9).')
            
            # Check for at least one special character
            if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password1):
                raise ValidationError('Password must contain at least one special character (!@#$%^&* etc).')
        
        return password2


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'profile_picture')


class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = RoleChangeRequest
        fields = ('requested_role', 'reason')
        widgets = {
            'requested_role': forms.RadioSelect(),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
