from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.books.models import Book
from .models import BorrowRequest

User = get_user_model()


def create_user(username='reader', **kwargs):
    # user model only accepts `role` as extra field
    if 'role' not in kwargs:
        kwargs.setdefault('role', 'reader')
    return User.objects.create_user(username=username, password='password', **kwargs)


def create_book(author):
    # supply all required fields with dummy data
    return Book.objects.create(
        title='Test Book',
        original_author='Original',
        author=author,
        description='A test book',
        genre='fiction',
        language='English',
        publication_date=timezone.now().date(),
        status='approved',
    )


class BorrowRequestTests(TestCase):
    def setUp(self):
        self.reader = create_user('reader')
        self.author = create_user('author', role='author')
        self.book = create_book(self.author)

    def test_request_with_duration_and_approval_sets_due_date(self):
        # reader logs in and posts a borrow request with 7 days
        self.client.login(username='reader', password='password')
        url = reverse('borrow_request_create', args=[self.book.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {'duration': '7'}
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, 'Book request submitted')
        br = BorrowRequest.objects.get(reader=self.reader, book=self.book)
        self.assertEqual(br.requested_days, 7)
        # approve the request as author
        self.client.logout()
        self.client.login(username='author', password='password')
        approve_url = reverse('borrow_request_approve', args=[br.pk])
        resp = self.client.post(approve_url, follow=True)
        br.refresh_from_db()
        self.assertEqual(br.status, 'approved')
        # due date should be ~7 days from today
        self.assertEqual(br.due_date, timezone.now().date() + timedelta(days=7))

    def test_default_period_if_none_selected(self):
        self.client.login(username='reader', password='password')
        url = reverse('borrow_request_create', args=[self.book.pk])
        # simulate user submitting the form without duration (should not normally happen)
        resp = self.client.post(url, {}, follow=True)
        self.assertContains(resp, 'Book request submitted')
        br = BorrowRequest.objects.get(reader=self.reader, book=self.book)
        self.assertIsNone(br.requested_days)
        self.client.logout()
        self.client.login(username='author', password='password')
        self.client.post(reverse('borrow_request_approve', args=[br.pk]))
        br.refresh_from_db()
        from django.conf import settings
        self.assertEqual(br.due_date, timezone.now().date() + timedelta(days=settings.BOOK_BORROW_DAYS))

class BorrowRequestViewerTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user(
            username='reader', password='pass', role='reader')
        self.author = User.objects.create_user(
            username='author', password='pass', role='author')
        self.book = Book.objects.create(
            title='Test PDF', author=self.author, description='d',
            genre='other', language='English', publication_date=timezone.now().date(),
            pdf_file=None,
            availability='borrow', status='approved'
        )

    def _create_request(self, days=7):
        br = BorrowRequest.objects.create(
            reader=self.reader, book=self.book, requested_days=days
        )
        br.approve_request()
        return br

    def test_viewer_endpoint_requires_authorization(self):
        url = reverse('book_viewer', args=[self.book.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.client.login(username='reader', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_viewer_with_approved_request(self):
        self.book.file_blob = b'%PDF-1.4\n%...'
        self.book.file_mime = 'application/pdf'
        self.book.save()
        self._create_request(days=7)
        self.client.login(username='reader', password='pass')
        resp = self.client.get(reverse('book_viewer', args=[self.book.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'This document is view-only')

    def test_file_endpoint_streams_only_with_permission(self):
        self.book.file_blob = b'%PDF-1.4\n%...'
        self.book.file_mime = 'application/pdf'
        self.book.save()
        url = reverse('book_file', args=[self.book.pk])
        self.client.login(username='reader', password='pass')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
        self._create_request(days=7)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn(b'%PDF-1.4', resp.content)
