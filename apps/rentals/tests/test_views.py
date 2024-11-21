from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rentals.models import Book, Rental
from django.utils import timezone
import json

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123'
        )
        # Create test book
        self.book = Book.objects.create(
            title="Test Book",
            author=json.dumps(["Test Author"]),
            page_count=300
        )

    def test_home_view(self):
        # Test unauthorized access
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test authorized access
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_book_collection_view(self):
        self.client.login(username='admin', password='admin123')

        # Test basic collection view
        response = self.client.get(reverse('book_collection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_collection.html')

        # Test search functionality
        response = self.client.get(f"{reverse('book_collection')}?search=Test")
        self.assertContains(response, "Test Book")

        # Test status filter
        response = self.client.get(f"{reverse('book_collection')}?status=available")
        self.assertContains(response, "Test Book")

    def test_student_list_view(self):
        self.client.login(username='admin', password='admin123')

        # Test basic list view
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_list.html')

        # Test search functionality
        response = self.client.get(f"{reverse('student_list')}?search=regular")
        self.assertContains(response, "regular")

        # Test filter
        response = self.client.get(f"{reverse('student_list')}?filter=with_rentals")
        self.assertEqual(response.status_code, 200)

    def test_rental_operations(self):
        self.client.login(username='admin', password='admin123')

        # Test creating new rental
        rental_data = {
            'user': self.regular_user.id,
            'book': self.book.id,
        }
        response = self.client.post(reverse('new_rental'), rental_data)
        self.assertEqual(Rental.objects.count(), 1)

        rental = Rental.objects.first()

        # Test extending rental
        response = self.client.post(reverse('extend_rental'), {'rental_id': rental.id})
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Test returning rental
        response = self.client.post(reverse('return_rental'), {'rental_id': rental.id})
        self.assertEqual(response.status_code, 302)
        updated_rental = Rental.objects.get(id=rental.id)
        self.assertIsNotNone(updated_rental.return_date)

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_view(self):
        # Test GET request
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        # Test successful login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Test failed login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertContains(response, 'Invalid credentials')

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout