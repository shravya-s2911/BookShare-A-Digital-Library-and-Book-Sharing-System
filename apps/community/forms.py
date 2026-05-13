from django import forms
from .models import Community, CommunityPost, Comment


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Community name',
                'style': 'color: #1a1a1a;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your community...',
                'rows': 4,
                'style': 'color: #1a1a1a;'
            }),
        }


class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'book']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Post title',
                'style': 'color: #1a1a1a;'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts...',
                'rows': 6,
                'style': 'color: #1a1a1a;'
            }),
            'book': forms.Select(attrs={
                'class': 'form-control',
                'style': 'color: #1a1a1a;'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment...',
                'rows': 3,
                'style': 'color: #1a1a1a;'
            }),
        }
