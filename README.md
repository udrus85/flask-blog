# Flask Blog

Демонстрационный проект блога на Flask для портфолио.

## 🎯 О проекте

Полноценный блог с системой аутентификации, постами, комментариями и тегами. Проект демонстрирует навыки работы с Flask и сопутствующими технологиями.

## 🛠 Технологии

- **Flask** - веб-фреймворк
- **Flask-SQLAlchemy** - ORM для работы с базой данных
- **Flask-Login** - управление сессиями пользователей
- **Flask-WTF** - формы с CSRF защитой
- **Flask-Migrate** - миграции базы данных
- **Bootstrap 5** - CSS фреймворк
- **SQLite** - база данных
- **pytest** - тестирование

## ✨ Функциональность

- 👤 Регистрация и аутентификация пользователей
- 🔐 Хеширование паролей (Werkzeug)
- 📝 CRUD операции для постов
- 💬 Система комментариев
- 🏷 Теги для постов
- 🔍 Поиск по постам
- 📄 Пагинация
- 👁 Счетчик просмотров
- 📋 Черновики постов
- 👤 Профили пользователей

## 📁 Структура проекта

```
flask-blog/
├── app/
│   ├── __init__.py      # Фабрика приложения (Application Factory)
│   ├── models.py        # Модели SQLAlchemy
│   ├── forms.py         # WTForms формы
│   ├── routes.py        # Маршруты (Blueprints)
│   ├── templates/       # Jinja2 шаблоны
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   └── posts/
│   └── static/          # CSS, JS
├── tests/
│   └── test_app.py      # Тесты pytest
├── config.py            # Конфигурации
├── run.py              # Точка входа
└── requirements.txt     # Зависимости
```

## 🚀 Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/flask-blog.git
cd flask-blog

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python run.py
```

Приложение будет доступно по адресу: http://localhost:5000

## 🧪 Тестирование

```bash
# Запуск тестов
pytest -v

# Запуск с покрытием
pytest --cov=app
```

## 💻 CLI команды

```bash
# Создать базу данных
flask create_db

# Заполнить тестовыми данными
flask seed_db

# Flask shell с контекстом
flask shell
```

## 📝 Паттерны и практики

- **Application Factory** - гибкое создание экземпляров приложения
- **Blueprints** - модульная организация маршрутов
- **Конфигурации** - разделение настроек для dev/test/prod
- **Формы WTForms** - валидация и CSRF защита
- **Хеширование паролей** - безопасное хранение
- **Пагинация** - эффективная работа с большими данными

## 📄 Лицензия

MIT License

