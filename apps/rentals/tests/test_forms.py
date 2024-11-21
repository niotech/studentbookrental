from django.test import TestCase
from django.contrib.auth.models import User
from rentals.models import Book
from rentals.forms import RentalForm
import json

class RentalFormTest(TestCase):
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

    def test_rental_form_valid_data(self):
        form_data = {
            'user': self.user.id,
            'book': self.book.id,
        }
        form = RentalForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_rental_form_no_data(self):
        form = RentalForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Both user and book are required