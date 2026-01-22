"""
Модели базы данных для Flask Blog.
Демонстрирует работу с Flask-SQLAlchemy и Flask-Login.
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Модель пользователя.
    Поддерживает аутентификацию через Flask-Login.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    bio = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Связи
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Хеширует и сохраняет пароль."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Загрузчик пользователя для Flask-Login."""
    return db.session.get(User, int(user_id))


class Post(db.Model):
    """
    Модель поста блога.
    Связана с пользователем и комментариями.
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)

    # Внешний ключ
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Связи
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='post_tags', backref=db.backref('posts', lazy='dynamic'))

    def increment_views(self):
        """Увеличивает счетчик просмотров."""
        self.views += 1
        db.session.commit()

    def __repr__(self):
        return f'<Post {self.title[:30]}>'


class Comment(db.Model):
    """
    Модель комментария к посту.
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    is_approved = db.Column(db.Boolean, default=True)

    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'


class Tag(db.Model):
    """
    Модель тега для постов.
    Связь many-to-many с постами.
    """
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'


# Таблица связи для many-to-many между постами и тегами
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

