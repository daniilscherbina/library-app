from .base import db, BaseModel
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

class BookReservation(BaseModel):
    __tablename__ = 'book_reservations'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    status = db.Column(db.String(50), default='active')
    return_date = db.Column(db.DateTime)  # Добавляем поле для даты возврата
    
    book = relationship('Book', back_populates='reservations')
    user = relationship('User', back_populates='reservations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'reservation_date': self.reservation_date.isoformat(),
            'expiry_date': self.expiry_date.isoformat(),
            'status': self.status,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'book': self.book.to_dict() if self.book else None,
            'user': self.user.to_dict() if self.user else None
        }
