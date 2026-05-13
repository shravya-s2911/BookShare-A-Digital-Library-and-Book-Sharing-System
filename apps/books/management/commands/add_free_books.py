from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.books.models import Book
from apps.users.models import User
from datetime import datetime


class Command(BaseCommand):
    help = 'Add freely available books from Project Gutenberg to the database'

    def handle(self, *args, **options):
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create an admin user first.'))
            return
        
        # List of free books from Project Gutenberg
        free_books = [
            {
                'title': 'Pride and Prejudice',
                'author_name': 'Jane Austen',
                'description': 'A romantic novel of manners written by Jane Austen in 1813. The novel follows the character development of Elizabeth Bennet, the protagonist of the book. Set in Georgian England, Pride and Prejudice explores the themes of marriage, morality, education, and family.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1813-01-28',
                'publisher': 'Project Gutenberg',
                'pages': 279,
            },
            {
                'title': 'Jane Eyre',
                'author_name': 'Charlotte Brontë',
                'description': 'Jane Eyre is a novel by English writer Charlotte Brontë. The novel follows the experiences of its protagonist, a young orphaned girl, as she progresses through life. It is a bildungsroman and early feminist novel.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1847-10-16',
                'publisher': 'Project Gutenberg',
                'pages': 507,
            },
            {
                'title': 'Wuthering Heights',
                'author_name': 'Emily Brontë',
                'description': 'Wuthering Heights is an English novel by Emily Brontë published under the pseudonym "Ellis Bell" in 1847. It is a wild, passionate novel set on the Yorkshire moors in Northern England, and tells the story of two families and their connections through time.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1847-12-19',
                'publisher': 'Project Gutenberg',
                'pages': 323,
            },
            {
                'title': 'Moby Dick',
                'author_name': 'Herman Melville',
                'description': 'Moby-Dick is an American novel by writer Herman Melville. The novel is narrated by Ishmael, a sailor new to the crew of the whaling ship Pequod. The book follows the voyage of the ship and its captain, Ahab, as he hunts the great white whale Moby Dick.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1851-10-18',
                'publisher': 'Project Gutenberg',
                'pages': 585,
            },
            {
                'title': 'Frankenstein',
                'author_name': 'Mary Shelley',
                'description': 'Frankenstein is a novel by English author Mary Shelley that was first published in 1818. The work is a gothic science fiction novel about Victor Frankenstein, a young scientist who becomes obsessed with creating life in the form of a hideous creature.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1818-01-01',
                'publisher': 'Project Gutenberg',
                'pages': 280,
            },
            {
                'title': "Alice's Adventures in Wonderland",
                'author_name': 'Lewis Carroll',
                'description': "Alice's Adventures in Wonderland is a novel written by Lewis Carroll that tells of a girl named Alice who falls through a rabbit hole into a subterranean fantasy world populated by peculiar, anthropomorphic creatures.",
                'genre': 'children',
                'language': 'English',
                'publication_date': '1865-11-26',
                'publisher': 'Project Gutenberg',
                'pages': 191,
            },
            {
                'title': 'The Picture of Dorian Gray',
                'author_name': 'Oscar Wilde',
                'description': 'The Picture of Dorian Gray is a philosophical novel by Oscar Wilde. It tells of a young man named Dorian Gray, the subject of a portrait, who becomes obsessed with his own beauty and begins to pursue a course of selfish and destructive behavior.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1890-07-01',
                'publisher': 'Project Gutenberg',
                'pages': 254,
            },
            {
                'title': 'The Great Gatsby',
                'author_name': 'F. Scott Fitzgerald',
                'description': 'The Great Gatsby is a novel of the Jazz Age that has been acclaimed by generations of readers. It is a tale of the American Dream and the roaring twenties, seen through the eyes of Nick Carraway, who is drawn into the world of the mysterious millionaire Jay Gatsby.',
                'genre': 'fiction',
                'language': 'English',
                'publication_date': '1925-04-10',
                'publisher': 'Project Gutenberg',
                'pages': 180,
            },
            {
                'title': '1984',
                'author_name': 'George Orwell',
                'description': '1984 is a dystopian social science fiction novel by the English writer George Orwell. It was published in 1949 and sets out an alarming and depressing vision of totalitarianism. The novel follows the life of Winston Smith, a low-ranking member of the ruling Party in London.',
                'genre': 'sci-fi',
                'language': 'English',
                'publication_date': '1949-06-08',
                'publisher': 'Project Gutenberg',
                'pages': 328,
            },
            {
                'title': 'The Adventures of Sherlock Holmes',
                'author_name': 'Arthur Conan Doyle',
                'description': 'A collection of twelve short stories featuring the detective Sherlock Holmes and his companion Dr. Watson as they solve various mysteries in Victorian London.',
                'genre': 'mystery',
                'language': 'English',
                'publication_date': '1892-06-30',
                'publisher': 'Project Gutenberg',
                'pages': 374,
            },
        ]
        
        added_count = 0
        for book_data in free_books:
            # Check if book already exists
            if Book.objects.filter(title=book_data['title']).exists():
                self.stdout.write(self.style.WARNING(f'Book "{book_data["title"]}" already exists. Skipping...'))
                continue
            
            # Create book
            book = Book.objects.create(
                title=book_data['title'],
                author=admin_user,
                description=book_data['description'],
                genre=book_data['genre'],
                language=book_data['language'],
                publication_date=book_data['publication_date'],
                publisher=book_data['publisher'],
                pages=book_data['pages'],
                availability='download',
                status='approved',  # Admin books are auto-approved
            )
            
            added_count += 1
            self.stdout.write(self.style.SUCCESS(f'✓ Added book: {book.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n{added_count} books added successfully!'))
