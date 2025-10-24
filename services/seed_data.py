from models import db, User, Book, Author, Genre, BookReservation
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_test_data():
    """Создание тестовых данных для всех таблиц"""
    
    # Проверяем, есть ли уже данные
    if Book.query.first() is not None:
        print("Тестовые данные уже существуют в базе.")
        return
    
    print("Создание тестовых данных...")
    
    # Создаем жанры
    genres_data = [
        {"name": "Роман", "description": "Большое повествовательное произведение"},
        {"name": "Фантастика", "description": "Научная фантастика и фэнтези"},
        {"name": "Детектив", "description": "Детективные истории и триллеры"},
        {"name": "Поэзия", "description": "Стихотворные произведения"},
        {"name": "Исторический", "description": "Исторические произведения"},
    ]
    
    genres = []
    for genre_data in genres_data:
        genre = Genre(**genre_data)
        db.session.add(genre)
        genres.append(genre)
    
    db.session.commit()
    print("Создано жанров:", len(genres))
    
    # Создаем авторов
    authors_data = [
        {"first_name": "Лев", "last_name": "Толстой", "biography": "Великий русский писатель", "birth_date": datetime(1828, 9, 9)},
        {"first_name": "Фёдор", "last_name": "Достоевский", "biography": "Классик русской литературы", "birth_date": datetime(1821, 11, 11)},
        {"first_name": "Александр", "last_name": "Пушкин", "biography": "Великий русский поэт", "birth_date": datetime(1799, 6, 6)},
        {"first_name": "Антон", "last_name": "Чехов", "biography": "Мастер короткого рассказа", "birth_date": datetime(1860, 1, 29)},
        {"first_name": "Николай", "last_name": "Гоголь", "biography": "Автор сатирических произведений", "birth_date": datetime(1809, 4, 1)},
    ]
    
    authors = []
    for author_data in authors_data:
        author = Author(**author_data)
        db.session.add(author)
        authors.append(author)
    
    db.session.commit()
    print("Создано авторов:", len(authors))
    
    # Создаем книги с разным количеством копий
    books_data = [
        {
            "title": "Война и мир",
            "description": "Роман-эпопея, описывающий русское общество в эпоху войн против Наполеона",
            "publication_year": 1869,
            "isbn": "978-5-699-12345-1",
            "total_copies": 5,
            "available_copies": 3
        },
        {
            "title": "Преступление и наказание",
            "description": "Роман о моральных страданиях бывшего студента Родиона Раскольникова",
            "publication_year": 1866,
            "isbn": "978-5-699-12345-2",
            "total_copies": 3,
            "available_copies": 1
        },
        {
            "title": "Евгений Онегин",
            "description": "Роман в стихах, одно из самых значительных произведений русской литературы",
            "publication_year": 1833,
            "isbn": "978-5-699-12345-3",
            "total_copies": 4,
            "available_copies": 4
        },
        {
            "title": "Вишнёвый сад",
            "description": "Пьеса о гибели дворянских гнёзд",
            "publication_year": 1904,
            "isbn": "978-5-699-12345-4",
            "total_copies": 2,
            "available_copies": 0  # Все забронированы
        },
        {
            "title": "Мёртвые души",
            "description": "Поэма, сатирическое изображение российского общества",
            "publication_year": 1842,
            "isbn": "978-5-699-12345-5",
            "total_copies": 3,
            "available_copies": 2
        },
        {
            "title": "Анна Каренина",
            "description": "Роман о трагической любви замужней женщины",
            "publication_year": 1877,
            "isbn": "978-5-699-12345-6",
            "total_copies": 4,
            "available_copies": 4
        },
        {
            "title": "Братья Карамазовы",
            "description": "Последний роман Достоевского, философская драма",
            "publication_year": 1880,
            "isbn": "978-5-699-12345-7",
            "total_copies": 2,
            "available_copies": 1
        },
        {
            "title": "Капитанская дочка",
            "description": "Исторический роман о пугачёвском восстании",
            "publication_year": 1836,
            "isbn": "978-5-699-12345-8",
            "total_copies": 3,
            "available_copies": 3
        },
    ]
    
    books = []
    for i, book_data in enumerate(books_data):
        book = Book(**book_data)
        # Назначаем авторов книгам
        book.authors.append(authors[i % len(authors)])
        if i < len(authors) - 1:
            book.authors.append(authors[(i + 1) % len(authors)])
        
        # Назначаем жанры
        book.genres.append(genres[i % len(genres)])
        book.genres.append(genres[(i + 1) % len(genres)])
        if i % 3 == 0:
            book.genres.append(genres[(i + 2) % len(genres)])
        
        db.session.add(book)
        books.append(book)
    
    db.session.commit()
    print("Создано книг:", len(books))
    
    # Создаем обычных пользователей
    users_data = [
        {"email": "reader1@example.com", "first_name": "Иван", "last_name": "Петров", "role": "reader"},
        {"email": "reader2@example.com", "first_name": "Мария", "last_name": "Иванова", "role": "reader"},
        {"email": "reader3@example.com", "first_name": "Алексей", "last_name": "Сидоров", "role": "reader"},
        {"email": "reader4@example.com", "first_name": "Елена", "last_name": "Кузнецова", "role": "reader"},
        {"email": "reader5@example.com", "first_name": "Дмитрий", "last_name": "Смирнов", "role": "reader"},
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        user.set_password("password123")
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    print("Создано пользователей:", len(users))
    
    # Создаем бронирования для книг с available_copies = 0
    for i in range(2):  # Создаем 2 бронирования для "Вишнёвого сада"
        reservation = BookReservation(
            book_id=4,  # ID "Вишнёвого сада"
            user_id=users[i].id,
            status="active",
            reservation_date=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            expiry_date=datetime.utcnow() + timedelta(days=random.randint(5, 14))
        )
        db.session.add(reservation)
    
    # Создаем несколько других бронирований с разными статусами
    other_reservations = [
        {"book_id": 2, "user_id": users[2].id, "status": "active"},  # Преступление и наказание
        {"book_id": 7, "user_id": users[3].id, "status": "active"},  # Братья Карамазовы
        {"book_id": 1, "user_id": users[4].id, "status": "completed", "return_date": datetime.utcnow() - timedelta(days=5)},  # Завершенное
        {"book_id": 3, "user_id": users[0].id, "status": "cancelled"},  # Отмененное
    ]
    
    for res_data in other_reservations:
        reservation = BookReservation(
            book_id=res_data["book_id"],
            user_id=res_data["user_id"],
            status=res_data["status"],
            reservation_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            expiry_date=datetime.utcnow() + timedelta(days=14),
            return_date=res_data.get("return_date")
        )
        db.session.add(reservation)
    
    db.session.commit()
    print("Создано бронирований")
    
    print("Тестовые данные успешно созданы!")
