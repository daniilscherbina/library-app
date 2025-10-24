from flask import Blueprint, request, jsonify
from models.base import db
from models.book import Book
from models.author import Author
from models.genre import Genre
import json

books_bp = Blueprint('books', __name__)

@books_bp.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    books = Book.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'books': [book.to_dict() for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'current_page': page
    })

@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@books_bp.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    
    book = Book(
        title=data['title'],
        description=data.get('description'),
        publication_year=data.get('publication_year'),
        isbn=data.get('isbn'),
        total_copies=data.get('total_copies', 1),
        available_copies=data.get('available_copies', data.get('total_copies', 1)),
        file_stub_metadata=json.dumps(data.get('file_stub_metadata')) if data.get('file_stub_metadata') else None
    )
    
    # Handle authors
    if 'author_ids' in data:
        authors = Author.query.filter(Author.id.in_(data['author_ids'])).all()
        book.authors = authors
    
    # Handle genres
    if 'genre_ids' in data:
        genres = Genre.query.filter(Genre.id.in_(data['genre_ids'])).all()
        book.genres = genres
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201

@books_bp.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    book.title = data.get('title', book.title)
    book.description = data.get('description', book.description)
    book.publication_year = data.get('publication_year', book.publication_year)
    book.isbn = data.get('isbn', book.isbn)
    book.total_copies = data.get('total_copies', book.total_copies)
    book.available_copies = data.get('available_copies', book.available_copies)
    
    if 'file_stub_metadata' in data:
        book.file_stub_metadata = json.dumps(data['file_stub_metadata'])
    
    # Update authors if provided
    if 'author_ids' in data:
        authors = Author.query.filter(Author.id.in_(data['author_ids'])).all()
        book.authors = authors
    
    # Update genres if provided
    if 'genre_ids' in data:
        genres = Genre.query.filter(Genre.id.in_(data['genre_ids'])).all()
        book.genres = genres
    
    db.session.commit()
    return jsonify(book.to_dict())

@books_bp.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return '', 204

@books_bp.route('/api/books/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'books': [], 'total': 0})
    
    books = Book.query.filter(
        Book.title.ilike(f'%{query}%') | 
        Book.description.ilike(f'%{query}%')
    ).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    })
