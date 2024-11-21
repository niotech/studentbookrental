import requests

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, logout, authenticate, login
from django.core.paginator import Paginator

from django.db.models import F, Q, Exists, OuterRef, ExpressionWrapper, DurationField
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Rental, Book
from .forms import RentalForm

from django.utils import timezone

User = get_user_model()

# def start_rental(request):
#     if request.method == 'POST':
#         form = RentalForm(request.POST)
#         if form.is_valid():
#             rental = form.save(commit=False)
#             # Fetch book details from OpenLibrary API
#             response = requests.get(f"https://openlibrary.org/search.json?title={rental.book.title}")
#             data = response.json()
#             if data['docs']:
#                 rental.book.page_count = data['docs'][0].get('number_of_pages', 0)
#                 rental.book.save()
#             rental.save()
#             return JsonResponse({'status': 'Rental started'})
#     else:
#         form = RentalForm()
#     return render(request, 'rentals/start_rental.html', {'form': form})

# def prolong_rental(request, rental_id):
#     rental = get_object_or_404(Rental, id=rental_id)
#     rental.return_date = timezone.now()
#     rental.save()
#     fee = rental.calculate_fee()
#     return JsonResponse({'status': 'Rental prolonged', 'fee': fee})

def is_admin(user):
    return user.is_staff

def fetch_book_details(title):
    url = f"https://openlibrary.org/search.json?title={title.replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['numFound'] > 0:
            book = data['docs'][0]
            return {
                'title': book.get('title', ''),
                'author': book.get('author_name', ['Unknown'])[0],
                'pages': book.get('number_of_pages_median') or book.get('number_of_pages', 100)
            }
    return None

@login_required
@user_passes_test(is_admin)
def home(request):
    current_time = timezone.now()
    rentals = Rental.objects.filter(return_date__isnull=True)

    students = User.objects.filter(is_staff=False)

    return render(request, 'home.html', {'rentals': rentals, 'students': students})

@login_required
@user_passes_test(is_admin)
def book_collection(request):
    # Get all books
    books_query = Book.objects.all()

    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        books_query = books_query.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )

    # Apply status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        current_time = timezone.now()
        rental_subquery = Rental.objects.filter(
            book=OuterRef('pk'),
            return_date__isnull=True
        )

        if status_filter == 'available':
            books_query = books_query.annotate(
                has_rental=Exists(rental_subquery)
            ).filter(has_rental=False)
        elif status_filter == 'rented':
            books_query = books_query.filter(
                rental__return_date__isnull=True,
                rental__rental_date__gt=current_time - timezone.timedelta(days=30)
            )
        elif status_filter == 'overdue':
            books_query = books_query.filter(
                rental__return_date__isnull=True,
                rental__rental_date__lte=current_time - timezone.timedelta(days=30)
            )

    # Order books
    books_query = books_query.order_by('title')

    # Paginate results
    paginator = Paginator(books_query, 9)  # Show 9 books per page
    page = request.GET.get('page')
    books = paginator.get_page(page)

    # Add current rental information to each book
    for book in books:
        book.current_rental = book.rental_set.filter(return_date__isnull=True).first()

    context = {
        'books': books,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'book_collection.html', context)


@login_required
@user_passes_test(is_admin)
def student_list(request):
    # Get all students (excluding staff/admin)
    students_query = User.objects.filter(is_staff=False).order_by('username')

    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        students_query = students_query.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Apply rental filters
    filter_type = request.GET.get('filter', '')
    if filter_type:
        rental_subquery = Rental.objects.filter(
            user=OuterRef('pk'),
            return_date__isnull=True
        )

        if filter_type == 'with_rentals':
            students_query = students_query.filter(
                Exists(rental_subquery)
            )
        elif filter_type == 'with_overdue':
            students_query = students_query.filter(
                Exists(rental_subquery.filter(
                    rental_date__lte=timezone.now() - timezone.timedelta(days=30)
                ))
            )

    # Paginate results
    paginator = Paginator(students_query, 10)  # Show 10 students per page
    page = request.GET.get('page')
    students = paginator.get_page(page)

    context = {
        'students': students,
        'search_query': search_query,
        'filter_type': filter_type,
    }

    return render(request, 'student_list.html', context)

@login_required
@user_passes_test(is_admin)
def extend_rental(request):
    if request.method == 'POST':
        rental_id = request.POST.get('rental_id')
        rental = get_object_or_404(Rental, id=rental_id)
        rental.rental_date = timezone.now()
        rental.save()
    return redirect('home')

@login_required
@user_passes_test(is_admin)
def return_rental(request):
    if request.method == 'POST':
        rental_id = request.POST.get('rental_id')
        rental = get_object_or_404(Rental, id=rental_id)
        rental.return_date = timezone.now()
        rental.save()
    return redirect('home')


@user_passes_test(is_admin)
def new_rental(request):
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            book_details = fetch_book_details(rental.book.title)
            if book_details:
                rental.book.page_count = book_details['pages']
                rental.book.save()
            rental.save()
            return redirect('home')
    else:
        form = RentalForm()
    return render(request, 'new_rental.html', {'form': form})

@user_passes_test(is_admin)
def student_history(request):
    student_id = request.GET.get('student')
    if student_id:
        student = get_object_or_404(User, id=student_id)
        rentals = Rental.objects.filter(user=student).order_by('-rental_date')
        return render(request, 'student_history.html', {
            'student': student,
            'rentals': rentals
        })
    return redirect('home')

@user_passes_test(is_admin)
def init_books(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'python django')
        Book.init_data(title)
        return redirect('home')
    return render(request, 'init_books.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')