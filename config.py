import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///library.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Yandex API Gateway URL
    OPEN_LIBRARY_API_GATEWAY_URL = os.getenv(
        'OPEN_LIBRARY_API_GATEWAY_URL', 
        'https://<api-gateway-id>.apigw.yandexcloud.net/open-library/search'
    )
    
    # Yandex SmartCaptcha
    SMARTCAPTCHA_SERVER_KEY = os.getenv('SMARTCAPTCHA_SERVER_KEY', '')
    SMARTCAPTCHA_CLIENT_KEY = os.getenv('SMARTCAPTCHA_CLIENT_KEY', '')
    
    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
