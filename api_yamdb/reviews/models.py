from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from .validators import validate_year


class User(AbstractUser):
    """User model for user"""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_USER = (
        ('user', USER),
        ('moderator', MODERATOR),
        ('admin', ADMIN),
    )
    password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    username = models.CharField(
        null=False,
        blank=False,
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(r'^[\w.@+-]+\Z'),
        ],
    )
    email = models.EmailField(
        null=False,
        blank=False,
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    bio = models.CharField(
        max_length=255,
    )
    role = models.CharField(
        max_length=32,
        choices=ROLE_USER,
        default='user',
        null=True,
        blank=True,
    )
    confirmation_code = models.CharField(
        'Код авторизации', max_length=6, blank=True, null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'username',
                    'email',
                ],
                name='unique_user',
            )
        ]

        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser or self.is_staff or self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(models.Model):
    """Category model for category"""

    name = models.CharField(
        'название категории',
        max_length=256,
        null=False,
        blank=False,
        help_text='название категории',
    )
    slug = models.CharField(
        'slug категории',
        max_length=50,
        null=False,
        blank=False,
        unique=True,
        help_text='slug категории',
        validators=[
            RegexValidator(r'^[-a-zA-Z0-9_]+$'),
        ],
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Genre model for genre"""

    name = models.CharField(
        'название жанра',
        max_length=256,
        null=False,
        blank=False,
        help_text='название жанра',
    )
    slug = models.SlugField(
        'slug жанра',
        max_length=50,
        null=False,
        blank=False,
        unique=True,
        help_text='slug жанра',
        validators=[
            RegexValidator(r'^[-a-zA-Z0-9_]+$'),
        ],
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Title model for title"""

    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска', validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Краткое описание произведения',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        through='GenreTitle',
        verbose_name='Жанр',
        related_name='titles',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Model for GenreTitle"""

    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title',
        verbose_name='Произведение',
    )
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        related_name='genre',
        verbose_name='Жанр',
    )

    def __str__(self):
        return f'{self.title_id}, {self.genre_id}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        related_name='reviews',
        verbose_name='произведение',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Отзыв',
    )
    author = models.ForeignKey(
        User,
        related_name='reviews',
        verbose_name='автор отзыва',
        on_delete=models.CASCADE,
    )
    score = models.SmallIntegerField(
        'Оценка',
        default=0,
        validators=[
            MaxValueValidator(10, 'Оценка должна быть не более 10'),
            MinValueValidator(1, 'Оценка должна быть не менее 1'),
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'
            )
        ]


class Comment(models.Model):
    """Comment model for comment"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания комментария',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f'{self.author.username[:15]}, {self.text[:30]}'
