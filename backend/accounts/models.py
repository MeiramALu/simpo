from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Lang(models.TextChoices):
    RU = 'ru', 'Русский'
    KK = 'kk', 'Қазақша'
    EN = 'en', 'English'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('email_verified', True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Участник симпозиума. Вход — по email, username не используется."""
    username = None
    first_name = None
    last_name = None

    email = models.EmailField('Email', unique=True)
    full_name = models.CharField('ФИО', max_length=255)
    organization = models.CharField('Организация', max_length=255, blank=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    lang = models.CharField('Язык', max_length=2, choices=Lang.choices, default=Lang.RU)
    email_verified = models.BooleanField('Email подтверждён', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.full_name} <{self.email}>'

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(' ')[0] if self.full_name else self.email
