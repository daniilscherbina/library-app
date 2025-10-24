from flask import Blueprint, request, jsonify, current_app
from services.open_library import get_open_library_service
from models.book import Book

web_versions_bp = Blueprint('web_versions', __name__)

@web_versions_bp.route('/api/books/<int:book_id>/web-versions', methods=['GET'])
def get_book_web_versions(book_id):
    """Получение веб-версий книги из Open Library"""
    
    open_library_service = get_open_library_service()
    
    if not open_library_service or not open_library_service.is_available():
        current_app.logger.warning("Сервис Open Library не доступен")
        return jsonify({
            'success': False,
            'error': 'Сервис поиска электронных версий временно недоступен',
            'service_available': False
        }), 503
    
    # Получаем параметр сортировки
    sort = request.args.get('sort', 'new')
    
    try:
        # Получаем книгу из базы данных
        book = Book.query.get_or_404(book_id)
        current_app.logger.info(f"Поиск электронных версий для книги: {book.title}")
        
        # Получаем веб-версии
        result = open_library_service.get_book_web_versions(book, sort=sort)
        
        # Добавляем информацию о сервисе
        result['service_available'] = True
        result['book_id'] = book_id
        result['book_title'] = book.title
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении веб-версий для книги {book_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}',
            'service_available': True,
            'book_id': book_id
        }), 500

@web_versions_bp.route('/api/web-versions/search', methods=['GET'])
def search_web_versions():
    """Поиск веб-версий по названию книги"""
    
    open_library_service = get_open_library_service()
    
    if not open_library_service or not open_library_service.is_available():
        return jsonify({
            'success': False,
            'error': 'Сервис поиска электронных версий временно недоступен',
            'service_available': False
        }), 503
    
    # Получаем параметры поиска
    title = request.args.get('title')
    sort = request.args.get('sort', 'new')
    
    if not title:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать название книги для поиска',
            'service_available': True
        }), 400
    
    try:
        # Выполняем поиск
        result = open_library_service.search_books_by_title(
            title=title,
            sort=sort
        )
        
        # Добавляем информацию о сервисе
        result['service_available'] = True
        result['search_query'] = title
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при поиске веб-версий для '{title}': {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}',
            'service_available': True,
            'search_query': title
        }), 500

@web_versions_bp.route('/api/web-versions/sort-options', methods=['GET'])
def get_sort_options():
    """Получение доступных опций сортировки"""
    
    return jsonify({
        'sort_options': [
            {'value': 'new', 'label': 'Новые издания'},
            {'value': 'editions', 'label': 'По количеству изданий'},
            {'value': 'relevance', 'label': 'По релевантности'}
        ],
        'service_available': get_open_library_service() is not None
    })

@web_versions_bp.route('/api/web-versions/status', methods=['GET'])
def get_service_status():
    """Получение статуса сервиса Open Library"""
    
    open_library_service = get_open_library_service()
    is_available = open_library_service and open_library_service.is_available()
    
    status_info = {
        'service_available': is_available,
        'service_name': 'Open Library Search',
        'timestamp': None
    }
    
    if is_available:
        status_info['cloud_function_url'] = open_library_service.cloud_function_url
        status_info['timestamp'] = '2024-01-01T00:00:00Z'  # Можно добавить реальное время
        
        # Простой тест доступности
        try:
            test_result = open_library_service.search_books_by_title('test', 'new')
            status_info['test_status'] = 'success' if test_result.get('success') else 'failed'
            status_info['test_error'] = test_result.get('error')
        except Exception as e:
            status_info['test_status'] = 'error'
            status_info['test_error'] = str(e)
    
    return jsonify(status_info)
