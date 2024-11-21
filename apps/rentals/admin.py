from django.contrib import admin
from .models import Book, Rental

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'page_count']
    search_fields = ['title', 'author']

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'rental_date', 'return_date', 'rental_cost']
    search_fields = ['book__title', 'user__username']
    list_filter = ['rental_date', 'return_date']

    def rental_cost(self, obj):
        return obj.calculate_fee()
