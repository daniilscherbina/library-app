from app import create_app
from models import db, User

def create_first_admin():
    app = create_app()
    
    with app.app_context():
        # Проверяем, есть ли уже администраторы
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # Создаем первого администратора
            admin = User(
                email='admin@library.com',
                first_name='Администратор',
                last_name='Системы',
                role='admin'
            )
            admin.set_password('admin123')  # Смените пароль после первого входа!
            
            db.session.add(admin)
            db.session.commit()
            print('Первый администратор создан!')
            print('Email: admin@library.com')
            print('Пароль: admin123')
            print('Обязательно смените пароль после первого входа!')
        else:
            print('Администратор уже существует в системе.')

if __name__ == '__main__':
    create_first_admin()
