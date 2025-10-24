from flask import Blueprint, request, jsonify
from models.base import db
from models.reservation import BookReservation
from models.book import Book
from datetime import datetime

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    
    # Проверяем доступность книги
    book = Book.query.get(data['book_id'])
    if not book or book.available_copies <= 0:
        return jsonify({'error': 'Книга недоступна для бронирования'}), 400
    
    # Проверяем, не забронировал ли пользователь уже эту книгу
    existing_reservation = BookReservation.query.filter_by(
        book_id=data['book_id'], 
        user_id=data['user_id'],
        status='active'
    ).first()
    
    if existing_reservation:
        return jsonify({'error': 'Пользователь уже забронировал эту книгу'}), 400
    
    reservation = BookReservation(
        book_id=data['book_id'],
        user_id=data['user_id']
    )
    
    # Уменьшаем количество доступных копий
    book.available_copies -= 1
    
    db.session.add(reservation)
    db.session.commit()
    
    return jsonify(reservation.to_dict()), 201

@reservations_bp.route('/api/reservations/user/<int:user_id>', methods=['GET'])
def get_user_reservations(user_id):
    reservations = BookReservation.query.filter_by(user_id=user_id).all()
    return jsonify([reservation.to_dict() for reservation in reservations])

@reservations_bp.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    reservation = BookReservation.query.get_or_404(reservation_id)
    
    # Возвращаем книгу в доступные
    reservation.book.available_copies += 1
    reservation.status = 'cancelled'
    
    db.session.commit()
    return '', 204

# Новый endpoint для возврата книги
@reservations_bp.route('/api/reservations/<int:reservation_id>/return', methods=['POST'])
def return_book(reservation_id):
    reservation = BookReservation.query.get_or_404(reservation_id)
    
    # Проверяем, что бронирование активно
    if reservation.status != 'active':
        return jsonify({'error': 'Бронирование уже завершено или отменено'}), 400
    
    # Возвращаем книгу в доступные
    reservation.book.available_copies += 1
    reservation.status = 'completed'
    reservation.return_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(reservation.to_dict())
