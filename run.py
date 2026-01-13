"""
Точка входа для запуска Flask приложения.
"""

import os
from app import create_app, db
from app.models import User, Post, Comment, Tag

# Создание приложения
app = create_app(os.environ.get('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    """Добавляет объекты в контекст Flask shell."""
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'Comment': Comment,
        'Tag': Tag
    }


@app.cli.command()
def create_db():
    """Создает таблицы в базе данных."""
    db.create_all()
    print('База данных создана!')


@app.cli.command()
def seed_db():
    """Заполняет базу данных тестовыми данными."""
    # Создаем тестового пользователя
    user = User(username='demo', email='demo@example.com')
    user.set_password('demo123')
    db.session.add(user)

    # Создаем теги
    tags = [Tag(name=name) for name in ['python', 'flask', 'web', 'tutorial']]
    db.session.add_all(tags)

    # Создаем тестовые посты
    posts = [
        Post(
            title='Добро пожаловать в Flask Blog!',
            content='Это первый пост в нашем блоге. Flask - отличный микрофреймворк для создания веб-приложений на Python.',
            author=user,
            tags=[tags[0], tags[1]]
        ),
        Post(
            title='Как начать работу с Flask',
            content='В этом посте мы рассмотрим основы Flask: маршрутизацию, шаблоны Jinja2, формы и работу с базой данных через SQLAlchemy.',
            author=user,
            tags=[tags[1], tags[2], tags[3]]
        )
    ]
    db.session.add_all(posts)
    db.session.commit()
    print('Тестовые данные добавлены!')


if __name__ == '__main__':
    app.run(debug=True)

