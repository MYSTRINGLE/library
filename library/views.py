from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Book
from .forms import BookModelForm


def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        )

    return render(request, 'library/book_list.html', {
        'books': books,
        'query': query,
    })


def add_book(request):
    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookModelForm()

    return render(request, 'library/book_form.html', {
        'form': form,
    })
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    return render(request, 'library/book_detail.html', {
        'book': book
    })

def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookModelForm(
            request.POST,
            request.FILES,
            instance=book
        )

        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookModelForm(instance=book)

    return render(request, 'library/book_form.html', {
        'form': form,
    })

def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.delete()
        return redirect('book_list')

    return render(request, 'library/book_confirm_delete.html', {
        'book': book,
    })
