from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rentals.models import Book, Rental
import json

class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author=json.dumps(["Test Author"]),
            page_count=300
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(json.loads(self.book.author), ["Test Author"])
        self.assertEqual(self.book.page_count, 300)

    def test_book_str_representation(self):
        self.assertEqual(str(self.book), "Test Book")

    def test_init_data_method(self):
        # Test the static method with a known book title
        Book.init_data("Python Programming")
        self.assertTrue(Book.objects.filter(title__icontains="Python").exists())


class RentalModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Test Book",
            author=json.dumps(["Test Author"]),
            page_count=300
        )
        self.rental = Rental.objects.create(
            user=self.user,
            book=self.book,
        )

        self.rental.rental_date=timezone.now() - timedelta(days=15)  # avoid auto_add_now=True

    def test_rental_creation(self):
        self.assertEqual(self.rental.user, self.user)
        self.assertEqual(self.rental.book, self.book)
        self.assertIsNone(self.rental.return_date)

    def test_rental_duration(self):
        self.assertTrue(14 <= self.rental.rental_duration <= 16)  # Allow for small timing differences

    def test_is_overdue_property(self):
        # Test not overdue
        self.assertFalse(self.rental.is_overdue)

        # Test overdue
        self.rental.rental_date = timezone.now() - timedelta(days=31)
        self.rental.save()
        self.assertTrue(self.rental.is_overdue)

    def test_calculate_fee(self):
        # Test no fee for first 30 days
        self.assertEqual(self.rental.calculate_fee(), 0)

        # Test fee calculation after 30 days
        self.rental.rental_date = timezone.now() - timedelta(days=45)
        self.rental.save()
        expected_fee = (self.book.page_count / 100)  # One month fee
        self.assertEqual(self.rental.calculate_fee(), expected_fee)

    def test_rental_manager_methods(self):
        # Test current rentals
        current_rentals = Rental.objects.current()
        self.assertEqual(current_rentals.count(), 1)

        # Test rental history
        self.rental.return_date = timezone.now()
        self.rental.save()
        history = Rental.objects.history()
        self.assertEqual(history.count(), 1)