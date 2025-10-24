import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///library.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # URL облачной функции Yandex Cloud
    OPEN_LIBRARY_FUNCTION_URL = os.getenv(
        'OPEN_LIBRARY_FUNCTION_URL', 
        'https://functions.yandexcloud.net/your-function-id'
    )

    SMARTCAPTCHA_SERVER_KEY = os.getenv('SMARTCAPTCHA_SERVER_KEY', '')
    SMARTCAPTCHA_CLIENT_KEY = os.getenv('SMARTCAPTCHA_CLIENT_KEY', '')
    
    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
