from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView
from flask import redirect, url_for, request, flash
from models.base import db
from models.user import User
from models.book import Book
from models.author import Author
from models.genre import Genre
from models.reservation import BookReservation
import json
from datetime import datetime

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        from flask import session
        return session.get('user') and session.get('user').get('role') == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Для доступа к админке необходимо войти как администратор', 'error')
        return redirect(url_for('web.login', next=request.url))

class BookModelView(ModelView):
    def is_accessible(self):
        from flask import session
        return session.get('user') and session.get('user').get('role') == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Для доступа к админке необходимо войти как администратор', 'error')
        return redirect(url_for('web.login', next=request.url))
    
    column_list = ['id', 'title', 'total_copies', 'available_copies', 'publication_year', 'isbn', 'created_at']
    column_searchable_list = ['title', 'isbn']
    column_filters = ['publication_year', 'created_at']
    column_editable_list = ['total_copies', 'available_copies']
    
    form_columns = ['title', 'description', 'publication_year', 'isbn', 
                   'total_copies', 'available_copies', 'file_stub_metadata', 'authors', 'genres']
    
    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'file_stub_metadata') and form.file_stub_metadata.data:
            try:
                json.loads(form.file_stub_metadata.data)
            except json.JSONDecodeError:
                raise ValueError("file_stub_metadata должен быть валидным JSON")
        
        # Гарантируем, что available_copies не превышает total_copies
        if model.available_copies > model.total_copies:
            model.available_copies = model.total_copies

class UserModelView(ModelView):
    def is_accessible(self):
        from flask import session
        return session.get('user') and session.get('user').get('role') == 'admin'
    
    column_list = ['id', 'email', 'first_name', 'last_name', 'role', 'membership_status', 'join_date']
    column_searchable_list = ['email', 'first_name', 'last_name']
    column_filters = ['role', 'membership_status', 'join_date']
    column_editable_list = ['role', 'membership_status']
    
    form_columns = ['email', 'password_hash', 'first_name', 'last_name', 'role', 'membership_status']
    
    def on_model_change(self, form, model, is_created):
        if is_created and form.password_hash.data:
            from werkzeug.security import generate_password_hash
            model.password_hash = generate_password_hash(form.password_hash.data)

class AuthorModelView(ModelView):
    def is_accessible(self):
        from flask import session
        return session.get('user') and session.get('user').get('role') == 'admin'
    
    column_list = ['id', 'first_name', 'last_name', 'birth_date']
    column_searchable_list = ['first_name', 'last_name']
    column_filters = ['birth_date']

class GenreModelView(ModelView):
    def is_accessible(self):
        from flask import session
        return session.get('user') and session.get('user').get('role') == 'admin'
    
    column_list = ['id', 'name', 'description']
    column_searchable_list = ['name']

class ReservationModelView(ModelView):
    def is_accessible(self):
        from flask import session
        return session.get('user') and session.get('user').get('role') == 'admin'
    
    column_list = ['id', 'book', 'user', 'reservation_date', 'expiry_date', 'return_date', 'status']
    column_filters = ['status', 'reservation_date', 'return_date']
    
    form_columns = ['book', 'user', 'reservation_date', 'expiry_date', 'return_date', 'status']
    
    def on_model_change(self, form, model, is_created):
        # При изменении статуса на "completed" устанавливаем дату возврата
        if model.status == 'completed' and not model.return_date:
            model.return_date = datetime.utcnow()
        
        # При отмене бронирования возвращаем книгу
        if model.status == 'cancelled' and model.book:
            model.book.available_copies += 1
        # При завершении бронирования возвращаем книгу
        elif model.status == 'completed' and model.book:
            model.book.available_copies += 1
        # При активации бронирования забираем книгу
        elif model.status == 'active' and model.book and is_created:
            model.book.available_copies -= 1
    
    def after_model_change(self, form, model, is_created):
        db.session.commit()
