from flask import Blueprint, jsonify
from services.open_library import get_open_library_service

api_gateway_bp = Blueprint('api_gateway', __name__)

@api_gateway_bp.route('/api/gateway/status', methods=['GET'])
def get_gateway_status():
    """Получение статуса API Gateway"""
    
    open_library_service = get_open_library_service()
    
    status_info = {
        'service_available': open_library_service is not None and open_library_service.is_available(),
        'service_type': 'api_gateway',
        'gateway_url': None,
        'health_status': None,
        'timestamp': None
    }
    
    if open_library_service and open_library_service.is_available():
        status_info['gateway_url'] = open_library_service.api_gateway_url
        status_info['health_status'] = open_library_service.health_check()
        status_info['timestamp'] = '2024-01-01T00:00:00Z'  # Можно добавить реальное время
    
    return jsonify(status_info)

@api_gateway_bp.route('/api/gateway/test', methods=['GET'])
def test_gateway():
    """Тестовый запрос к API Gateway"""
    
    open_library_service = get_open_library_service()
    
    if not open_library_service or not open_library_service.is_available():
        return jsonify({
            'success': False,
            'error': 'Сервис Open Library не настроен',
            'service_type': 'api_gateway'
        }), 503
    
    # Тестовый запрос
    test_title = "The Lord of the Rings"
    result = open_library_service.search_books_by_title(test_title)
    
    return jsonify({
        'test_query': test_title,
        'gateway_url': open_library_service.api_gateway_url,
        'result': result
    })
