import html
import requests
import unicodedata

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def normalize_string(original_string):
    return unicodedata.normalize("NFKC", html.unescape(original_string))



class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.JSONField(blank=True, null=True)
    page_count = models.IntegerField()

    def __str__(self):
        return self.title

    @staticmethod
    def init_data(title='python django'):
        API_URL = f"https://openlibrary.org/search.json?title={title}"
        response = requests.get(API_URL)
        if response.status_code == 200:
            numFound = response.json()['numFound']
            if numFound == 0:
                print(f"Searched for '{title}' return 0 Book")
                return
            for doc in response.json()['docs']:
                number_of_pages = doc.get('number_of_pages') or doc.get('number_of_pages_median', 100)  # Not all Book in the API resu=lt has number_of_pages_median or number_of_pages attribute in JSON data returned, so assuming 100 as default number of pages so it can be calculated for rental cost

                author_name = None  # not all Book in the API result has author_name attribut, default to None
                if 'author_name' in doc:
                    for i, v in enumerate(doc['author_name']):
                        doc['author_name'][i] = normalize_string(v)
                    author_name = doc['author_name']
                obj, created = Book.objects.update_or_create(title=normalize_string(doc['title']), author=author_name, page_count=number_of_pages)
                if created:
                    print(f"Adding Book '{obj.title}' by '{obj.author}'")
                else:
                    print(f"Updating Book '{obj.title}' by '{obj.author}'")
        else:
            print(f"API request issue, code = {response.status_code}")

class RentalManager(models.Manager):
    def current(self):
        return self.filter(return_date__isnull=True).order_by('rental_date')

    def history(self):
        return self.filter(return_date__isnull=False).order_by('-return_date')

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    objects = RentalManager()

    @property
    def rental_duration(self):
        """
        Calculate the duration of the rental in days.
        If the book is returned, calculate until return_date.
        If not returned, calculate until current time.
        """
        end_date = self.return_date if self.return_date else timezone.now()
        duration = (end_date - self.rental_date).days
        return duration

    @property
    def is_overdue(self):
        """
        Check if the rental is overdue (more than 30 days and not returned).
        Returns True if the book is overdue, False otherwise.
        """
        if self.return_date:
            return False
        return self.rental_duration > 30

    def calculate_fee(self):
        current_date = timezone.now()
        rental_duration = (current_date - self.rental_date).days

        # No fee for first 30 days
        if rental_duration <= 30:
            return 0

        # Calculate months beyond the first month
        extra_months = ((rental_duration - 30) + 29) // 30  # Round up to nearest month
        monthly_fee = self.book.page_count / 100

        return extra_months * monthly_fee
