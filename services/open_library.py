import requests
import json
from flask import current_app
import logging

class OpenLibraryService:
    """Сервис для работы с Open Library API через Yandex Cloud Function"""
    
    def __init__(self, cloud_function_url):
        self.cloud_function_url = cloud_function_url
        self.logger = logging.getLogger(__name__)
    
    def search_books_by_title(self, title, sort='new'):
        """
        Поиск книг в Open Library только по названию
        
        Args:
            title (str): Название книги
            sort (str): Способ сортировки ('new', 'editions', 'relevance')
            
        Returns:
            dict: Результаты поиска
        """
        
        if not title:
            return {
                'success': False,
                'error': 'Необходимо указать название книги'
            }
        
        # Формируем параметры запроса
        params = {
            'title': title,
            'sort': sort
        }
        
        try:
            self.logger.info(f"Вызов облачной функции: {self.cloud_function_url}")
            self.logger.info(f"Параметры поиска: title={title}, sort={sort}")
            
            # Вызываем облачную функцию
            response = requests.get(
                self.cloud_function_url,
                params=params,
                timeout=15
            )
            
            self.logger.info(f"Ответ облачной функции: статус {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Успешный ответ, найдено результатов: {data.get('total_results', 0)}")
                return data
            else:
                error_msg = f'Ошибка облачной функции: {response.status_code}'
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f'Ошибка подключения: {str(e)}'
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except json.JSONDecodeError as e:
            error_msg = f'Неверный формат ответа от сервера: {str(e)}'
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f'Неожиданная ошибка: {str(e)}'
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_book_web_versions(self, book, sort='new'):
        """
        Получение веб-версий для книги из базы данных
        
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
        return self.cloud_function_url is not None

# Создаем экземпляр сервиса
open_library_service = None

def init_open_library_service(app):
    """Инициализация сервиса Open Library"""
    global open_library_service
    cloud_function_url = app.config.get('OPEN_LIBRARY_FUNCTION_URL')
    
    if cloud_function_url and cloud_function_url != 'https://functions.yandexcloud.net/your-function-id':
        open_library_service = OpenLibraryService(cloud_function_url)
        app.logger.info(f"Open Library service initialized with URL: {cloud_function_url}")
    else:
        app.logger.warning("OPEN_LIBRARY_FUNCTION_URL not set or is default, Open Library service disabled")
        # Создаем заглушку для разработки
        open_library_service = None

def get_open_library_service():
    """Получение экземпляра сервиса Open Library"""
    return open_library_service
