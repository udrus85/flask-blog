"""
Тесты для Flask Blog приложения.
Демонстрирует навыки тестирования с pytest.
"""

import pytest
from app import create_app, db
from app.models import User, Post, Comment, Tag


@pytest.fixture
def app():
    """Создает тестовое приложение."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Тестовый клиент."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Тестовый CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Создает тестового пользователя."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


class TestUserModel:
    """Тесты модели User."""

    def test_password_hashing(self, app):
        """Тест хеширования паролей."""
        with app.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('secret')

            assert user.password_hash is not None
            assert user.password_hash != 'secret'
            assert user.check_password('secret')
            assert not user.check_password('wrong')

    def test_user_creation(self, app):
        """Тест создания пользователя."""
        with app.app_context():
            user = User(username='newuser', email='new@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            saved_user = User.query.filter_by(username='newuser').first()
            assert saved_user is not None
            assert saved_user.email == 'new@test.com'

    def test_user_repr(self, app):
        """Тест строкового представления."""
        with app.app_context():
            user = User(username='reprtest', email='repr@test.com')
            assert 'reprtest' in repr(user)


class TestPostModel:
    """Тесты модели Post."""

    def test_post_creation(self, app, sample_user):
        """Тест создания поста."""
        with app.app_context():
            user = User.query.get(sample_user)
            post = Post(
                title='Test Post',
                content='Test content',
                author=user
            )
            db.session.add(post)
            db.session.commit()

            saved_post = Post.query.filter_by(title='Test Post').first()
            assert saved_post is not None
            assert saved_post.author.username == 'testuser'
            assert saved_post.views == 0

    def test_increment_views(self, app, sample_user):
        """Тест увеличения счетчика просмотров."""
        with app.app_context():
            user = User.query.get(sample_user)
            post = Post(title='View Test', content='Content', author=user)
            db.session.add(post)
            db.session.commit()

            assert post.views == 0
            post.increment_views()
            assert post.views == 1
            post.increment_views()
            assert post.views == 2

    def test_post_tags(self, app, sample_user):
        """Тест связи постов с тегами."""
        with app.app_context():
            user = User.query.get(sample_user)
            tag1 = Tag(name='python')
            tag2 = Tag(name='flask')
            post = Post(title='Tagged Post', content='Content', author=user)
            post.tags.extend([tag1, tag2])

            db.session.add_all([tag1, tag2, post])
            db.session.commit()

            saved_post = Post.query.filter_by(title='Tagged Post').first()
            assert len(saved_post.tags) == 2
            assert 'python' in [t.name for t in saved_post.tags]


class TestCommentModel:
    """Тесты модели Comment."""

    def test_comment_creation(self, app, sample_user):
        """Тест создания комментария."""
        with app.app_context():
            user = User.query.get(sample_user)
            post = Post(title='Post', content='Content', author=user)
            comment = Comment(content='Test comment', author=user, post=post)

            db.session.add_all([post, comment])
            db.session.commit()

            assert post.comments.count() == 1
            assert post.comments.first().content == 'Test comment'


class TestRoutes:
    """Тесты маршрутов."""

    def test_index_page(self, client):
        """Тест главной страницы."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Flask Blog' in response.data.decode()

    def test_about_page(self, client):
        """Тест страницы 'О проекте'."""
        response = client.get('/about')
        assert response.status_code == 200
        assert 'О проекте' in response.data.decode()

    def test_login_page(self, client):
        """Тест страницы входа."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert 'Вход' in response.data.decode()

    def test_register_page(self, client):
        """Тест страницы регистрации."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert 'Регистрация' in response.data.decode()

    def test_search_empty(self, client):
        """Тест поиска без запроса."""
        response = client.get('/search')
        assert response.status_code == 200

    def test_protected_route_redirect(self, client):
        """Тест редиректа для защищенных маршрутов."""
        response = client.get('/posts/new')
        assert response.status_code == 302  # Redirect to login


class TestAuthentication:
    """Тесты аутентификации."""

    def test_register_user(self, client, app):
        """Тест регистрации нового пользователя."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None

    def test_login_logout(self, client, app, sample_user):
        """Тест входа и выхода."""
        # Вход
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Выход
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_invalid_login(self, client, sample_user):
        """Тест неверного логина."""
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert 'Неверный email или пароль' in response.data.decode()

