from .base import db, BaseModel
from sqlalchemy.orm import relationship

class Author(BaseModel):
    __tablename__ = 'authors'
    
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    
    books = relationship('Book', secondary='book_authors', back_populates='authors')
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'biography': self.biography,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None
        }
