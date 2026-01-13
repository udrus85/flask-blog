"""
WTForms формы для Flask Blog.
Демонстрирует работу с Flask-WTF.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

from app.models import User


class RegistrationForm(FlaskForm):
    """Форма регистрации нового пользователя."""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Это поле обязательно'),
        Length(min=3, max=64, message='Имя должно быть от 3 до 64 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Это поле обязательно'),
        Email(message='Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Это поле обязательно'),
        Length(min=6, message='Пароль должен быть минимум 6 символов')
    ])
    password2 = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Это поле обязательно'),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, field):
        """Проверка уникальности имени пользователя."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Это имя пользователя уже занято')

    def validate_email(self, field):
        """Проверка уникальности email."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Этот email уже зарегистрирован')


class LoginForm(FlaskForm):
    """Форма входа в систему."""
    email = StringField('Email', validators=[
        DataRequired(message='Это поле обязательно'),
        Email(message='Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Это поле обязательно')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class PostForm(FlaskForm):
    """Форма создания/редактирования поста."""
    title = StringField('Заголовок', validators=[
        DataRequired(message='Это поле обязательно'),
        Length(max=200, message='Максимум 200 символов')
    ])
    content = TextAreaField('Содержание', validators=[
        DataRequired(message='Это поле обязательно')
    ])
    tags = StringField('Теги (через запятую)', validators=[
        Optional()
    ])
    is_published = BooleanField('Опубликовать', default=True)
    submit = SubmitField('Сохранить')


class CommentForm(FlaskForm):
    """Форма добавления комментария."""
    content = TextAreaField('Комментарий', validators=[
        DataRequired(message='Это поле обязательно'),
        Length(min=3, max=1000, message='Комментарий должен быть от 3 до 1000 символов')
    ])
    submit = SubmitField('Отправить')


class ProfileForm(FlaskForm):
    """Форма редактирования профиля пользователя."""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Это поле обязательно'),
        Length(min=3, max=64, message='Имя должно быть от 3 до 64 символов')
    ])
    bio = TextAreaField('О себе', validators=[
        Optional(),
        Length(max=500, message='Максимум 500 символов')
    ])
    submit = SubmitField('Сохранить')


class SearchForm(FlaskForm):
    """Форма поиска постов."""
    query = StringField('Поиск', validators=[
        DataRequired(message='Введите поисковый запрос')
    ])
    submit = SubmitField('Искать')

