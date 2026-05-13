from django import forms
from .models import Book, BookWishlist


class BookForm(forms.ModelForm):
    # Optional upload field to store file directly into the database
    upload_file = forms.FileField(
        required=False,
        label='Upload file (PDF / EPUB)',
        widget=forms.ClearableFileInput(attrs={
            'accept': '.pdf,.epub,application/pdf,application/epub+zip'
        })
    )
    class Meta:
        model = Book
        fields = ('title', 'original_author', 'description', 'genre', 'language', 'publication_date', 
                  'publisher', 'isbn', 'pages', 'cover_image', 'pdf_file', 'availability')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['isbn'].help_text = 'Optional: ISBN-10 or ISBN-13'
        self.fields['pages'].help_text = 'Optional: Number of pages'
        # Make the model FileField accept pdf/epub in the browser file picker
        if 'pdf_file' in self.fields:
            self.fields['pdf_file'].widget.attrs.update({'accept': '.pdf,.epub,application/pdf,application/epub+zip'})
            # give clearer help text for download option
            self.fields['pdf_file'].help_text = self.fields['pdf_file'].help_text or ''
            self.fields['pdf_file'].help_text += ' (Accepted: PDF, EPUB)'

    def clean(self):
        cleaned_data = super().clean()
        availability = cleaned_data.get('availability')
        pdf_file = cleaned_data.get('pdf_file')
        upload_file = None
        if hasattr(self, 'files'):
            upload_file = self.files.get('upload_file') or self.files.get('pdf_file')

        # Require a file when availability allows borrowing or download
        required_avail = ['borrow', 'download', 'both']
        if availability in required_avail and not pdf_file and not upload_file:
            self.add_error('pdf_file', 'A PDF or EPUB file is required when the book is available for borrowing or download (provide via the form file field or upload_file).')

        # Validate file types if provided (accept only .pdf and .epub)
        def is_allowed(upload):
            if not upload:
                return True
            name = getattr(upload, 'name', '') or ''
            content_type = getattr(upload, 'content_type', '') or ''
            name = name.lower()
            if name.endswith('.pdf'):
                return True
            if name.endswith('.epub'):
                return True
            # fallback to checking mime
            if 'pdf' in content_type:
                return True
            if 'epub' in content_type:
                return True
            return False

        # Check pdf_file
        if pdf_file and not is_allowed(pdf_file):
            self.add_error('pdf_file', 'Only PDF or EPUB files are allowed.')

        # Check upload_file
        if upload_file and upload_file is not pdf_file and not is_allowed(upload_file):
            # attach error to the pdf_file field so it's visible in the form
            self.add_error('pdf_file', 'Only PDF or EPUB files are allowed in the upload.')
            
        return cleaned_data


class BookSearchForm(forms.Form):
    SORT_CHOICES = (
        ('-created_at', 'Newest First'),
        ('title', 'Title (A-Z)'),
        ('-title', 'Title (Z-A)'),
        ('publication_date', 'Publication Date (Oldest)'),
        ('-publication_date', 'Publication Date (Newest)'),
    )
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by title, author, or keywords',
            'class': 'form-control'
        })
    )
    
    genre = forms.MultipleChoiceField(
        choices=Book.GENRE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    
    availability = forms.MultipleChoiceField(
        choices=Book.AVAILABILITY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )
    
    language = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by language',
            'class': 'form-control'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.RadioSelect()
    )
