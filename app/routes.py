"""
Маршруты (routes) для Flask Blog.
Демонстрирует использование Blueprints для организации кода.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, Post, Comment, Tag
from app.forms import (
    RegistrationForm, LoginForm, PostForm, CommentForm,
    ProfileForm, SearchForm
)

# Создание Blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
posts_bp = Blueprint('posts', __name__)


# ==================== MAIN ROUTES ====================

@main_bp.route('/')
def index():
    """Главная страница с последними постами."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    return render_template('index.html', posts=posts)


@main_bp.route('/about')
def about():
    """Страница 'О проекте'."""
    return render_template('about.html')


@main_bp.route('/search')
def search():
    """Поиск постов."""
    query = request.args.get('q', '')
    if query:
        posts = Post.query.filter(
            Post.title.ilike(f'%{query}%') | Post.content.ilike(f'%{query}%'),
            Post.is_published == True
        ).order_by(Post.created_at.desc()).all()
    else:
        posts = []
    return render_template('search.html', posts=posts, query=query)


# ==================== AUTH ROUTES ====================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('Неверный email или пароль', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Профиль пользователя."""
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        # Проверка уникальности username
        existing = User.query.filter(
            User.username == form.username.data,
            User.id != current_user.id
        ).first()
        if existing:
            flash('Это имя пользователя уже занято', 'error')
        else:
            current_user.username = form.username.data
            current_user.bio = form.bio.data
            db.session.commit()
            flash('Профиль обновлен', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', form=form)


@auth_bp.route('/user/<username>')
def user_posts(username):
    """Посты конкретного пользователя."""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id, is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    return render_template('user_posts.html', user=user, posts=posts)


# ==================== POSTS ROUTES ====================

@posts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_post():
    """Создание нового поста."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            is_published=form.is_published.data,
            author=current_user
        )

        # Обработка тегов
        if form.tags.data:
            tag_names = [t.strip().lower() for t in form.tags.data.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)

        db.session.add(post)
        db.session.commit()
        flash('Пост успешно создан!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))

    return render_template('posts/create.html', form=form)


@posts_bp.route('/<int:post_id>')
def view_post(post_id):
    """Просмотр поста."""
    post = Post.query.get_or_404(post_id)
    if not post.is_published and (not current_user.is_authenticated or current_user.id != post.user_id):
        abort(404)

    post.increment_views()
    form = CommentForm()

    page = request.args.get('page', 1, type=int)
    comments = post.comments.filter_by(is_approved=True)\
        .order_by(Comment.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)

    return render_template('posts/view.html', post=post, form=form, comments=comments)


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Редактирование поста."""
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    form = PostForm(obj=post)
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in post.tags])

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.is_published = form.is_published.data

        # Обновление тегов
        post.tags.clear()
        if form.tags.data:
            tag_names = [t.strip().lower() for t in form.tags.data.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)

        db.session.commit()
        flash('Пост обновлен!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))

    return render_template('posts/edit.html', form=form, post=post)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Удаление поста."""
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Пост удален', 'info')
    return redirect(url_for('main.index'))


@posts_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Добавление комментария к посту."""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            author=current_user,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')

    return redirect(url_for('posts.view_post', post_id=post_id))


@posts_bp.route('/tag/<tag_name>')
def posts_by_tag(tag_name):
    """Посты по тегу."""
    tag = Tag.query.filter_by(name=tag_name.lower()).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = tag.posts.filter_by(is_published=True)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    return render_template('posts/by_tag.html', tag=tag, posts=posts)


@posts_bp.route('/my')
@login_required
def my_posts():
    """Посты текущего пользователя (включая черновики)."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id)\
        .order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    return render_template('posts/my_posts.html', posts=posts)

