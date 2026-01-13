"""
Flask Blog Application - Фабрика приложения.
Демонстрирует использование Application Factory pattern.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import config

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """
    Фабрика приложения Flask.

    Args:
        config_name: Имя конфигурации ('development', 'testing', 'production')

    Returns:
        Настроенный экземпляр Flask приложения
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Регистрация blueprints
    from app.routes import main_bp, auth_bp, posts_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp, url_prefix='/posts')

    # Создание таблиц при первом запуске
    with app.app_context():
        db.create_all()

    return app

