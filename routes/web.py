from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models.base import db
from models.user import User
from models.book import Book
from models.author import Author
from models.reservation import BookReservation
from services.captcha import get_captcha_service
from datetime import datetime

web_bp = Blueprint('web', __name__)

def get_captcha_context():
    """Получение контекста для капчи"""
    captcha_service = get_captcha_service()
    return {
        'captcha_enabled': captcha_service and captcha_service.is_configured(),
        'captcha_client_key': current_app.config.get('SMARTCAPTCHA_CLIENT_KEY', '')
    }

# Главная страница
@web_bp.route('/')
def index():
    books = Book.query.limit(10).all()
    return render_template('index.html', books=books, user=session.get('user'))

# Страница регистрации
@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    captcha_context = get_captcha_context()
    
    if request.method == 'POST':
        # Проверяем капчу, если она включена
        if captcha_context['captcha_enabled']:
            captcha_service = get_captcha_service()
            captcha_token = request.form.get('smart-token')
            
            if not captcha_token:
                flash('Пожалуйста, подтвердите, что вы не робот', 'error')
                return render_template('register.html', **captcha_context)
            
            # Проверяем токен капчи
            captcha_result = captcha_service.verify_captcha(captcha_token)
            if not captcha_result['success']:
                flash('Не удалось подтвердить, что вы не робот. Пожалуйста, попробуйте еще раз.', 'error')
                return render_template('register.html', **captcha_context)
        
        # Получаем данные формы
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form.get('role', 'reader')
        
        # Проверяем, существует ли пользователь
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('register.html', **captcha_context)
        
        # Создаем нового пользователя
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('web.login'))
    
    return render_template('register.html', **captcha_context)

# Страница входа
@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    captcha_context = get_captcha_context()
    
    if request.method == 'POST':
        # Проверяем капчу, если она включена
        if captcha_context['captcha_enabled']:
            captcha_service = get_captcha_service()
            captcha_token = request.form.get('smart-token')
            
            if not captcha_token:
                flash('Пожалуйста, подтвердите, что вы не робот', 'error')
                return render_template('login.html', **captcha_context)
            
            # Проверяем токен капчи
            captcha_result = captcha_service.verify_captcha(captcha_token)
            if not captcha_result['success']:
                flash('Не удалось подтвердить, что вы не робот. Пожалуйста, попробуйте еще раз.', 'error')
                return render_template('login.html', **captcha_context)
        
        # Получаем данные формы
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
            flash(f'Добро пожаловать, {user.first_name}!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.index'))
            return redirect(url_for('web.index'))
        else:
            flash('Неверный email или пароль', 'error')
    
    return render_template('login.html', **captcha_context)

# Выход
@web_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('web.index'))

# Страница всех книг
@web_bp.route('/books')
def books():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    books_pagination = Book.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('books.html', 
                         books=books_pagination.items,
                         pagination=books_pagination,
                         user=session.get('user'))

# Детали книги
@web_bp.route('/books/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book, user=session.get('user'))

# Бронирование книги
@web_bp.route('/books/<int:book_id>/reserve', methods=['POST'])
def reserve_book(book_id):
    if 'user_id' not in session:
        flash('Для бронирования книги необходимо войти в систему', 'error')
        return redirect(url_for('web.login'))
    
    book = Book.query.get_or_404(book_id)
    
    # Проверяем, доступна ли книга
    if book.available_copies <= 0:
        flash('Все экземпляры этой книги сейчас забронированы', 'error')
        return redirect(url_for('web.book_detail', book_id=book_id))
    
    # Проверяем, не забронировал ли пользователь уже эту книгу
    existing_reservation = BookReservation.query.filter_by(
        book_id=book_id, 
        user_id=session['user_id'],
        status='active'
    ).first()
    
    if existing_reservation:
        flash('Вы уже забронировали эту книгу', 'error')
        return redirect(url_for('web.book_detail', book_id=book_id))
    
    # Создаем бронирование
    reservation = BookReservation(
        book_id=book_id,
        user_id=session['user_id']
    )
    
    # Уменьшаем количество доступных копий
    book.available_copies -= 1
    
    db.session.add(reservation)
    db.session.commit()
    
    flash('Книга успешно забронирована!', 'success')
    return redirect(url_for('web.profile'))

# Профиль пользователя
@web_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Для просмотра профиля необходимо войти в систему', 'error')
        return redirect(url_for('web.login'))
    
    user_id = session['user_id']
    reservations = BookReservation.query.filter_by(user_id=user_id).order_by(
        BookReservation.created_at.desc()
    ).all()
    
    return render_template('profile.html', 
                         reservations=reservations, 
                         user=session.get('user'))

# Отмена бронирования
@web_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
def cancel_reservation(reservation_id):
    if 'user_id' not in session:
        flash('Для выполнения этого действия необходимо войти в систему', 'error')
        return redirect(url_for('web.login'))
    
    reservation = BookReservation.query.get_or_404(reservation_id)
    
    # Проверяем, принадлежит ли бронирование текущему пользователю
    if reservation.user_id != session['user_id']:
        flash('У вас нет прав для отмены этого бронирования', 'error')
        return redirect(url_for('web.profile'))
    
    # Возвращаем книгу в доступные
    reservation.book.available_copies += 1
    reservation.status = 'cancelled'
    
    db.session.commit()
    
    flash('Бронирование отменено', 'success')
    return redirect(url_for('web.profile'))

# Возврат книги
@web_bp.route('/reservations/<int:reservation_id>/return', methods=['POST'])
def return_book(reservation_id):
    if 'user_id' not in session:
        flash('Для выполнения этого действия необходимо войти в систему', 'error')
        return redirect(url_for('web.login'))
    
    reservation = BookReservation.query.get_or_404(reservation_id)
    
    # Проверяем, принадлежит ли бронирование текущему пользователю
    if reservation.user_id != session['user_id']:
        flash('У вас нет прав для возврата этой книги', 'error')
        return redirect(url_for('web.profile'))
    
    # Проверяем, что бронирование активно
    if reservation.status != 'active':
        flash('Это бронирование уже завершено или отменено', 'error')
        return redirect(url_for('web.profile'))
    
    # Возвращаем книгу в доступные
    reservation.book.available_copies += 1
    reservation.status = 'completed'
    reservation.return_date = datetime.utcnow()
    
    db.session.commit()
    
    flash('Книга успешно возвращена!', 'success')
    return redirect(url_for('web.profile'))

# Создание администратора
@web_bp.route('/admin/create-admin', methods=['GET', 'POST'])
def create_admin():
    if not session.get('user') or session.get('user').get('role') != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('web.login'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('create_admin.html')
        
        admin_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        flash('Администратор успешно создан!', 'success')
        return redirect(url_for('web.index'))
    
    return render_template('create_admin.html')
