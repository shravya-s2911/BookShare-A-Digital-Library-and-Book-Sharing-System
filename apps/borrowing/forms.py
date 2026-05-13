from django import forms
from .models import BorrowRequest


class BorrowRequestForm(forms.ModelForm):
    duration = forms.ChoiceField(
        choices=BorrowRequest.DURATION_CHOICES,
        label='Borrow period',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = BorrowRequest
        fields = ('duration',)

    def clean_duration(self):
        # allow blank - use default later
        val = self.cleaned_data.get('duration')
        if not val:
            return None
        try:
            return int(val)
        except (TypeError, ValueError):
            raise forms.ValidationError('Invalid duration')


class BorrowRequestRejectForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='Optional: Reason for rejection'
    )
