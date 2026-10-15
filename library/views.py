from django.http import request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Book
from .forms import BookModelForm

# 1. Book List View
def book_list(request):
    books = Book.objects.all()
    # Remove 'library/' so it looks directly inside the templates folder
    return render(request, 'library/book_list.html', {'page_obj': books})

 




# 2. Book Detail View
def book_detail(request, pk):
    """
    Display detailed information about a single book, plus similar titles.
    """
    book = get_object_or_404(
        Book.objects.select_related('author', 'publisher'),
        pk=pk,
    )
    
    similar_books = Book.objects.filter(
        genre=book.genre
    ).exclude(pk=book.pk).order_by('-rating')[:4]
    
    context = {
        'book': book,
        'similar_books': similar_books,
    }
    return render(request, 'book_detail.html', {'book': book})

# 3. Book Create View (Section 5b)
@login_required
def book_create(request):
    """
    Create a new book. GET displays the empty form. POST processes it.
    """
    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            book = form.save(commit=False)
            if hasattr(book, 'created_by'):
                book.created_by = request.user
            book.save()
            form.save_m2m()
            messages.success(request, f'"{book.title}" was added to the library.')
            return redirect('library:book_detail', pk=book.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookModelForm(user=request.user)
        
    return render(request, 'library/book_form.html', {
        'form': form,
        'title': 'Add a Book',
        'submit_text': 'Create Book',
    })


# 4. Book Update View (Section 5b)
@login_required
def book_update(request, pk):
    """
    Update an existing book. Only the creator or staff may edit it.
    """
    book = get_object_or_404(Book, pk=pk)
    
    if not request.user.is_staff and book.created_by != request.user:
        raise PermissionDenied("You don't have permission to edit this book.")
        
    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES, instance=book, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{book.title}" was updated.')
            return redirect('library:book_detail', pk=book.pk)
    else:
        form = BookModelForm(instance=book, user=request.user)
        
    return render(request, 'library/book_form.html', {
        'form': form,
        'title': 'Update Book',
        'submit_text': 'Update Book',
    })


# 4. Book Delete View
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('library:book_list')  # Adjust name if your list route differs
    return render(request, 'book_confirm_delete.html', {'book': book})
