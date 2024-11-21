from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_collection, name='book_collection'),
    path('students/', views.student_list, name='student_list'),
    path('new-rental/', views.new_rental, name='new_rental'),
    path('extend-rental/', views.extend_rental, name='extend_rental'),
    path('return-rental/', views.return_rental, name='return_rental'),
    path('student-history/', views.student_history, name='student_history'),
    path('init-books/', views.init_books, name='init_books'),
    path('accounts/login/', views.login_view, name='login'),  # Update this line
    path('logout/', views.logout_view, name='logout'),
]
