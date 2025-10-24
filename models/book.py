from .base import db, BaseModel
from sqlalchemy.orm import relationship
import json
from datetime import datetime

class Book(BaseModel):
    __tablename__ = 'books'
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    publication_year = db.Column(db.Integer)
    isbn = db.Column(db.String(20))
    file_stub_metadata = db.Column(db.Text)  # JSON stored as TEXT
    total_copies = db.Column(db.Integer, default=1)  # Общее количество копий
    available_copies = db.Column(db.Integer, default=1)  # Доступные копии
    # Убираем поле status, так как теперь статус определяется по available_copies
    
    authors = relationship('Author', secondary='book_authors', back_populates='books')
    genres = relationship('Genre', secondary='book_genres', back_populates='books')
    reservations = relationship('BookReservation', back_populates='book')
    
    @property
    def status(self):
        """Вычисляемый статус на основе доступных копий"""
        if self.available_copies > 0:
            return 'available'
        else:
            return 'reserved'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publication_year': self.publication_year,
            'isbn': self.isbn,
            'file_stub_metadata': json.loads(self.file_stub_metadata) if self.file_stub_metadata else None,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'status': self.status,
            'authors': [author.to_dict() for author in self.authors],
            'genres': [genre.to_dict() for genre in self.genres]
        }

# Association tables
book_authors = db.Table('book_authors',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete='CASCADE')),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id', ondelete='CASCADE')),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

book_genres = db.Table('book_genres',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id', ondelete='CASCADE')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE')),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
