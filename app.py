from flask import Flask, jsonify
from config import Config
from services.database import init_db
from services.open_library import init_open_library_service
from services.captcha import init_captcha_service
from services.seed_data import create_test_data
from routes.books import books_bp
from routes.authors import authors_bp
from routes.users import users_bp
from routes.reservations import reservations_bp
from routes.web import web_bp
from routes.web_versions import web_versions_bp
from admin.models import MyAdminIndexView, BookModelView, UserModelView, AuthorModelView, GenreModelView, ReservationModelView
from flask_admin import Admin
from models import db, User, Book, Author, Genre, BookReservation
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Настройка логирования
    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', 'INFO'),
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # Initialize database
    init_db(app)
    
    # Initialize Open Library service
    init_open_library_service(app)

    init_captcha_service(app)
    
    # Инициализация Flask-Admin
    admin = Admin(app, name='Библиотека - Админка', template_mode='bootstrap3', index_view=MyAdminIndexView())
    
    # Добавляем представления для моделей
    admin.add_view(BookModelView(Book, db.session, name='Книги'))
    admin.add_view(UserModelView(User, db.session, name='Пользователи'))
    admin.add_view(AuthorModelView(Author, db.session, name='Авторы'))
    admin.add_view(GenreModelView(Genre, db.session, name='Жанры'))
    admin.add_view(ReservationModelView(BookReservation, db.session, name='Бронирования'))
    
    # Register blueprints
    app.register_blueprint(books_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(web_versions_bp)
    
    # Обработчик ошибок для 404
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 'Ресурс не найден'
        }), 404
    
    # Обработчик ошибок для 500
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

    with app.app_context():
        # Проверяем, есть ли уже администраторы
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # Создаем первого администратора
            admin_user = User(
                email='admin@library.com',
                first_name='Администратор',
                last_name='Системы',
                role='admin'
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info('Первый администратор создан!')
            app.logger.info('Email: admin@library.com')
            app.logger.info('Пароль: admin123')
        else:
            app.logger.info('Администратор уже существует в системе.')
        
        # Создаем тестовые данные, если их нет
        create_test_data()
        
        # Логируем статус сервиса Open Library
        from services.open_library import get_open_library_service
        ol_service = get_open_library_service()
        if ol_service and ol_service.is_available():
            app.logger.info('Сервис Open Library инициализирован и доступен')
        else:
            app.logger.warning('Сервис Open Library недоступен')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
