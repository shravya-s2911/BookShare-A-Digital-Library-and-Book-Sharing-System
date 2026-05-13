from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'content')
        widgets = {
            'rating': forms.RadioSelect(),
            'content': forms.Textarea(attrs={'rows': 5}),
        }
