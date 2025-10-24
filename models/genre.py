from .base import db, BaseModel
from sqlalchemy.orm import relationship

class Genre(BaseModel):
    __tablename__ = 'genres'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    books = relationship('Book', secondary='book_genres', back_populates='genres')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
