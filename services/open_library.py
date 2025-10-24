import requests
import json
from flask import current_app
import logging

class OpenLibraryService:
    """Сервис для работы с Open Library API через Yandex API Gateway"""
    
    def __init__(self, api_gateway_url):
        self.api_gateway_url = api_gateway_url
        self.logger = logging.getLogger(__name__)
    
    def search_books_by_title(self, title, sort='new'):
        """
        Поиск книг в Open Library через API Gateway
        
        Args:
            title (str): Название книги
            sort (str): Способ сортировки ('new', 'editions', 'relevance')
            
        Returns:
            dict: Результаты поиска
        """
        
        if not title:
            return {
                'success': False,
                'error': 'Необходимо указать название книги',
                'service_type': 'api_gateway'
            }
        
        # Формируем параметры запроса
        params = {
            'title': title,
            'sort': sort
        }
        
        try:
            self.logger.info(f"Вызов API Gateway: {self.api_gateway_url}")
            self.logger.info(f"Параметры поиска: title={title}, sort={sort}")
            
            # Вызываем API Gateway
            response = requests.get(
                self.api_gateway_url,
                params=params,
                timeout=15
            )
            
            self.logger.info(f"Ответ API Gateway: статус {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Успешный ответ, найдено результатов: {data.get('total_results', 0)}")
                data['service_type'] = 'api_gateway'
                return data
            elif response.status_code == 400:
                error_msg = 'Неверные параметры запроса'
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'service_type': 'api_gateway'
                }
            else:
                error_msg = f'Ошибка API Gateway: {response.status_code}'
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'service_type': 'api_gateway'
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f'Ошибка подключения к API Gateway: {str(e)}'
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'service_type': 'api_gateway'
            }
        except json.JSONDecodeError as e:
            error_msg = f'Неверный формат ответа от API Gateway: {str(e)}'
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'service_type': 'api_gateway'
            }
        except Exception as e:
            error_msg = f'Неожиданная ошибка: {str(e)}'
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'service_type': 'api_gateway'
            }
    
    def get_book_web_versions(self, book, sort='new'):
        """
        Получение веб-версий для книги из базы данных через API Gateway
        
        Args:
            book: Объект книги из БД
            sort (str): Способ сортировки результатов
            
        Returns:
            dict: Информация о веб-версиях
        """
        
        # Используем только название книги для поиска
        return self.search_books_by_title(
            title=book.title,
            sort=sort
        )
    
    def is_available(self):
        """Проверка доступности сервиса"""
        return self.api_gateway_url is not None
    
    def health_check(self):
        """Проверка здоровья API Gateway"""
        try:
            health_url = self.api_gateway_url.replace('/open-library/search', '/health')
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except:
            return False

# Создаем экземпляр сервиса
open_library_service = None

def init_open_library_service(app):
    """Инициализация сервиса Open Library с API Gateway"""
    global open_library_service
    api_gateway_url = app.config.get('OPEN_LIBRARY_API_GATEWAY_URL')
    
    if api_gateway_url and api_gateway_url != 'https://<api-gateway-id>.apigw.yandexcloud.net/open-library/search':
        open_library_service = OpenLibraryService(api_gateway_url)
        
        # Проверяем доступность API Gateway
        if open_library_service.health_check():
            app.logger.info(f"Open Library service initialized with API Gateway: {api_gateway_url}")
        else:
            app.logger.warning(f"API Gateway health check failed, but service initialized: {api_gateway_url}")
    else:
        app.logger.warning("OPEN_LIBRARY_API_GATEWAY_URL not set or is default, Open Library service disabled")
        open_library_service = None

def get_open_library_service():
    """Получение экземпляра сервиса Open Library"""
    return open_library_service
