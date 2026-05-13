# BookShare - Digital Library Book Sharing System

A comprehensive Django-based digital library and book sharing platform where users can browse, share, borrow, and review books. The system supports multiple user roles including Readers, Authors, and Administrators.

## Features

### User Management
- **User Registration & Authentication**: Secure user registration with validation and email verification
- **Multiple User Roles**: Reader, Author, and Admin with different permissions
- **Profile Management**: Users can edit their profiles, upload profile pictures, and manage account settings
- **Role Change Requests**: Users can request to change their role with admin approval

### Book Management
- **Browse & Search**: Users can browse and search for books by title, author, genre, or keywords
- **Advanced Filters**: Filter books by genre, availability, language, and publication date
- **Book Details**: Comprehensive book information including cover images, descriptions, ratings, and reviews
- **Author Functionality**: Authors can publish books, manage their catalog, and view reader interactions
- **Admin Approval**: All new books require admin approval before they become available

### Borrowing System
- **Book Borrowing**: Readers can request to borrow books directly from authors
- **Request Management**: Authors can approve or reject borrow requests with optional reasons
- **Due Date Tracking**: Automatic tracking of borrow due dates with notifications for overdue items
- **Return Management**: Easy marking of books as returned

### Reviews & Ratings
- **Write Reviews**: Users can leave detailed reviews and ratings (1-5 stars) for books
- **View Reviews**: Display of all reviews with ratings and user information
- **Edit/Delete Reviews**: Users can edit or delete their own reviews
- **Average Ratings**: Automatic calculation and display of average book ratings

### Additional Features
- **Wishlist**: Users can add books to their wishlist for future reference
- **Reading History**: Track books read and mark them as completed
- **Notifications**: System for user notifications about requests and updates
- **Admin Panel**: Comprehensive admin dashboard for managing users, books, and requests
- **Responsive Design**: Mobile-friendly interface that works on all devices

## Tech Stack

- **Backend**: Django 4.2.0
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Python**: 3.8+

## Project Structure

```
edu_project/
├── config/                 # Django project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── apps/                  # Django applications
│   ├── users/             # User management and authentication
│   │   ├── models.py      # User and RoleChangeRequest models
│   │   ├── views.py       # Authentication and profile views
│   │   ├── forms.py       # Registration and login forms
│   │   ├── urls.py        # User app URLs
│   │   └── admin.py       # Django admin configuration
│   ├── books/             # Book management
│   │   ├── models.py      # Book, BookWishlist, ReadingHistory models
│   │   ├── views.py       # Book CRUD and dashboard views
│   │   ├── forms.py       # Book and search forms
│   │   ├── urls.py        # Book app URLs
│   │   └── admin.py       # Django admin configuration
│   ├── reviews/           # Review and rating system
│   │   ├── models.py      # Review model
│   │   ├── views.py       # Review CRUD views
│   │   ├── forms.py       # Review form
│   │   ├── urls.py        # Review app URLs
│   │   └── admin.py       # Django admin configuration
│   ├── borrowing/         # Book borrowing system
│   │   ├── models.py      # BorrowRequest model
│   │   ├── views.py       # Borrow request handling views
│   │   ├── forms.py       # Borrow forms
│   │   ├── urls.py        # Borrowing app URLs
│   │   └── admin.py       # Django admin configuration
│   └── core/              # Core utilities and notifications
│       ├── models.py      # Notification model
│       ├── context_processors.py  # Context processors
│       ├── utils.py       # Helper functions
│       └── admin.py       # Django admin configuration
├── templates/             # HTML templates
│   ├── base/              # Base template
│   ├── users/             # User-related templates
│   ├── books/             # Book-related templates
│   ├── reviews/           # Review templates
│   └── borrowing/         # Borrowing templates
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── media/                 # User-uploaded files
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
cd edu_project
```

### Step 2: Create a Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create an Admin User
```bash
python manage.py create_admin
```
This will prompt you to enter admin credentials. Follow the prompts to create an admin account.

Alternatively, use Django's default createsuperuser command:
```bash
python manage.py createsuperuser
```

### Step 6: Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Usage

### For Readers
1. **Register** as a Reader
2. **Browse** books using the book list or search functionality
3. **View** detailed book information including reviews and ratings
4. **Request** to borrow books from authors
5. **Leave** reviews and ratings for books you've read
6. **Manage** your borrowed books and reading history
7. **Create** a wishlist of books you want to read

### For Authors
1. **Register** as an Author
2. **Add** new books to the system with details and cover images
3. **Manage** your published books (edit, delete, view)
4. **Review** borrow requests from readers
5. **Approve or Reject** borrow requests with optional reasons
6. **View** reader interactions (reviews, ratings)
7. **Update** your profile and manage account settings

### For Administrators
1. **Login** with admin credentials
2. **Access** the admin dashboard for system overview
3. **Review** and approve/reject book upload requests
4. **Manage** user accounts and roles
5. **Handle** role change requests from users
6. **Monitor** system activity and user interactions
7. **Manage** user permissions and access levels

## Default Demo Accounts

After running `python manage.py create_admin`, you can log in with the credentials you created.

## API Endpoints & URL Routes

### Authentication
- `/users/register/` - User registration
- `/users/login/` - User login
- `/users/logout/` - User logout
- `/users/profile/` - View profile
- `/users/profile/edit/` - Edit profile
- `/users/password-change/` - Change password
- `/users/role-change-request/` - Request role change

### Books
- `/books/` - Browse all books
- `/books/search/` - Search books
- `/books/<id>/` - View book details
- `/books/add/` - Add new book (authors)
- `/books/<id>/edit/` - Edit book (authors)
- `/books/<id>/delete/` - Delete book (authors)
- `/books/author/books/` - View author's books
- `/books/author/dashboard/` - Author dashboard
- `/books/reader/dashboard/` - Reader dashboard
- `/books/admin/dashboard/` - Admin dashboard
- `/books/admin/book-requests/` - Manage book requests
- `/books/admin/users/` - Manage users
- `/books/admin/role-requests/` - Manage role requests

### Reviews
- `/reviews/add/<book_id>/` - Add review
- `/reviews/<id>/edit/` - Edit review
- `/reviews/<id>/delete/` - Delete review

### Borrowing
- `/borrowing/request/<book_id>/` - Request to borrow book
- `/borrowing/<id>/approve/` - Approve borrow request (authors)
- `/borrowing/<id>/reject/` - Reject borrow request (authors)
- `/borrowing/<id>/return/` - Return borrowed book
- `/borrowing/<id>/cancel/` - Cancel pending request

## Security Features

- **CSRF Protection**: All forms protected against Cross-Site Request Forgery
- **Password Security**: Passwords validated for strength (minimum 8 characters)
- **Authentication**: Secure user authentication and session management
- **Authorization**: Role-based access control for different user types
- **Input Validation**: Server-side validation for all user inputs
- **SQL Injection Prevention**: Using Django ORM to prevent SQL injection attacks
- **XSS Prevention**: Template auto-escaping to prevent Cross-Site Scripting

## Email Configuration

Currently, the application uses Django's console email backend for development. For production, configure SMTP settings in `config/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Database Models

### User Model
- Custom User model extending Django's AbstractUser
- Fields: username, email, password, role, bio, profile_picture, favorite_genres, is_approved, created_at, updated_at

### Book Model
- Fields: title, author, description, genre, language, publication_date, publisher, ISBN, cover_image, pdf_file, availability, status, pages, created_at, updated_at
- Methods: is_available_for_borrowing(), is_available_for_download(), is_published()

### Review Model
- Fields: book, reviewer, rating (1-5), title, content, created_at, updated_at
- Unique constraint: One review per user per book

### BorrowRequest Model
- Fields: reader, book, status, requested_at, approved_at, due_date, returned_at, reason_for_rejection
- Methods: is_overdue(), days_remaining(), approve_request(), reject_request(), return_book()

### Notification Model
- Fields: user, notification_type, title, message, related_book, related_user, is_read, created_at

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
python manage.py runserver 8080
```

### Database Errors
If you encounter database errors, try:
```bash
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
Collect static files:
```bash
python manage.py collectstatic
```

## Future Enhancements

- [ ] Email notifications for book availability and request updates
- [ ] Book discussion forums and comments
- [ ] Reading challenges and events
- [ ] Integration with external book APIs (Google Books, Open Library)
- [ ] PDF viewer for downloading books
- [ ] Mobile app (React Native or Flutter)
- [ ] Advanced recommendation algorithm
- [ ] Social sharing features
- [ ] Multi-language support
- [ ] Performance optimization for large datasets

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support & Help

For issues, questions, or suggestions, please:
- Check existing issues first
- Create a detailed issue description
- Include steps to reproduce the problem
- Provide error messages and screenshots if applicable

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Django community for the excellent framework
- Bootstrap for the responsive UI components
- All contributors who have helped with code, testing, and suggestions

---

**Last Updated**: February 2024  
**Version**: 1.0.0
