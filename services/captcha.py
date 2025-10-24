import requests
import json
from flask import request, current_app

class CaptchaService:
    """Сервис для работы с Yandex SmartCaptcha"""
    
    def __init__(self, server_key):
        self.server_key = server_key
        self.validation_url = "https://smartcaptcha.yandexcloud.net/validate"
    
    def verify_captcha(self, token, user_ip=None):
        """
        Проверка токена капчи
        
        Args:
            token (str): Токен от капчи
            user_ip (str): IP адрес пользователя
            
        Returns:
            dict: Результат проверки
        """
        if not token:
            return {
                'success': False,
                'error': 'Токен капчи отсутствует'
            }
        
        # Если IP не передан, пытаемся получить из запроса
        if not user_ip:
            user_ip = self._get_user_ip()
        
        try:
            # Отправляем запрос на валидацию
            response = requests.post(
                self.validation_url,
                data={
                    'secret': self.server_key,
                    'token': token,
                    'ip': user_ip
                },
                timeout=5
            )
            
            # Парсим ответ
            result = response.json()
            
            if response.status_code == 200:
                return {
                    'success': result.get('status') == 'ok',
                    'status': result.get('status'),
                    'message': result.get('message'),
                    'host': result.get('host')
                }
            else:
                current_app.logger.error(f"Captcha validation error: {response.status_code} - {result}")
                return {
                    'success': False,
                    'error': f'Ошибка сервера капчи: {response.status_code}',
                    'status': 'error'
                }
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Captcha request failed: {str(e)}")
            return {
                'success': False,
                'error': f'Ошибка подключения к сервису капчи: {str(e)}',
                'status': 'error'
            }
        except json.JSONDecodeError as e:
            current_app.logger.error(f"Captcha response parse error: {str(e)}")
            return {
                'success': False,
                'error': 'Неверный формат ответа от сервиса капчи',
                'status': 'error'
            }
    
    def _get_user_ip(self):
        """Получение IP адреса пользователя с учетом прокси"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_configured(self):
        """Проверка настройки капчи"""
        return bool(self.server_key)

# Создаем экземпляр сервиса
captcha_service = None

def init_captcha_service(app):
    """Инициализация сервиса капчи"""
    global captcha_service
    server_key = app.config.get('SMARTCAPTCHA_SERVER_KEY')
    
    if server_key:
        captcha_service = CaptchaService(server_key)
        app.logger.info("Captcha service initialized")
    else:
        app.logger.warning("SMARTCAPTCHA_SERVER_KEY not set, captcha service disabled")
        captcha_service = None

def get_captcha_service():
    """Получение экземпляра сервиса капчи"""
    return captcha_service
