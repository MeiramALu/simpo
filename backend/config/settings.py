"""
Настройки бэкенда Al-Farabi Global Symposium 2026.

Все чувствительные значения берутся из переменных окружения (или из файла .env
рядом с manage.py). Пример — в .env.example.
"""
import os
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path):
    """Простейший загрузчик .env без внешних зависимостей."""
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / '.env')


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    return str(env(key, default)).lower() in ('1', 'true', 'yes', 'on')


def env_list(key, default=''):
    return [x.strip() for x in env(key, default).split(',') if x.strip()]


SECRET_KEY = env('DJANGO_SECRET_KEY', 'dev-insecure-change-me')
DEBUG = env_bool('DJANGO_DEBUG', True)
ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'accounts',
    'registrations',
    'papers',
    'payments',
    'speakers',
    'program',
    'siteconfig',  # после остальных: создаёт роли с их правами
    'frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'config.middleware.ApiLanguageMiddleware',  # API — на языке посетителя, админка — по-русски
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # переопределения шаблонов админки
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- База данных: SQLite по умолчанию, PostgreSQL при DB_ENGINE=postgres ---
if env('DB_ENGINE') == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', 'afgs'),
            'USER': env('DB_USER', 'afgs'),
            'PASSWORD': env('DB_PASSWORD', ''),
            'HOST': env('DB_HOST', 'localhost'),
            'PORT': env('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': env('SQLITE_PATH', BASE_DIR / 'db.sqlite3'),
        }
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Языки: те же, что во фронте ---
LANGUAGE_CODE = 'ru'
LANGUAGES = [('ru', 'Русский'), ('kk', 'Қазақша'), ('en', 'English')]
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Загруженные статьи и квитанции. Наружу напрямую НЕ раздаются —
# только через API с проверкой владельца.
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(env('MEDIA_ROOT', BASE_DIR / 'media'))
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- DRF ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '2000/hour',
        # с одного IP: в университете много людей сидит за одним адресом
        'registration': '30/hour',
        'auth': '60/hour',
    },
    'DEFAULT_PAGINATION_CLASS': None,
}

# --- CORS: если фронт размещён на другом домене ---
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS

# --- Почта ---
EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', '')
EMAIL_PORT = int(env('EMAIL_PORT', '587'))
EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'Al-Farabi Symposium <al-farabi@kaznu.kz>')
# Куда приходят уведомления о новых заявках, статьях и оплатах
ORGANIZERS_EMAILS = env_list('ORGANIZERS_EMAILS', 'al-farabi@kaznu.kz')

# Адрес фронта — для ссылок в письмах (сброс пароля, подтверждение почты, возврат после оплаты)
FRONTEND_URL = env('FRONTEND_URL', 'http://127.0.0.1:8000').rstrip('/')

# --- Начальные значения. Дальше всё это меняется в админке:
#     «Настройки симпозиума» и «Публикационные взносы». ---
# Публикации и взносы (из раздела «Публикации» фронта)
PUBLICATION_FEES = {
    'proceedings': (Decimal('0'), 'KZT'),
    'tuva': (Decimal('300'), 'USD'),
    'vestnik_philosophy': (Decimal('60000'), 'KZT'),
    'vestnik_religion': (Decimal('60000'), 'KZT'),
    'vestnik_pedagogy': (Decimal('60000'), 'KZT'),
    'vestnik_psychology': (Decimal('60000'), 'KZT'),
}
# На каких статусах статьи можно платить взнос
PAYABLE_PAPER_STATUSES = env_list('PAYABLE_PAPER_STATUSES', 'accepted')
PAPER_MAX_UPLOAD_MB = 20
# Подавать статьи и платить можно только с подтверждённой почтой
REQUIRE_VERIFIED_EMAIL = env_bool('REQUIRE_VERIFIED_EMAIL', True)

# --- Оплата ---
# manual — счёт/реквизиты + загрузка квитанции, подтверждает оргкомитет в админке.
# test   — фиктивная касса для разработки. Работает только при PAYMENTS_TEST_MODE=true
#          (это жёсткий предохранитель: из админки на боевом сервере её не включить).
PAYMENT_PROVIDERS = env_list('PAYMENT_PROVIDERS', 'manual,test')
PAYMENTS_TEST_MODE = env_bool('PAYMENTS_TEST_MODE', DEBUG)
PAYMENT_BANK_DETAILS = {
    'recipient': env('BANK_RECIPIENT', 'НАО «Казахский национальный университет имени аль-Фараби»'),
    'bin': env('BANK_BIN', ''),
    'iik': env('BANK_IIK', ''),
    'bank': env('BANK_NAME', ''),
    'bik': env('BANK_BIK', ''),
    'kbe': env('BANK_KBE', ''),
    'knp': env('BANK_KNP', ''),
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
