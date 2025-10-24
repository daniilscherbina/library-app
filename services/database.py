from models.base import db
from models.book import Book, book_authors, book_genres
from models.author import Author
from models.genre import Genre
from models.user import User
from models.reservation import BookReservation

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
