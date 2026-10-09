from django.utils import translation

from .i18n import LANGS


def _pick(accept_language):
    """'en-US,en;q=0.9,ru;q=0.8' → 'en'. Неизвестный язык → английский (сайт международный)."""
    for part in accept_language.split(','):
        code = part.split(';')[0].strip().lower()[:2]
        if code in LANGS:
            return code
    return 'en'


class AdminLoginThrottleMiddleware:
    """
    Подбор пароля к админке: не больше 10 попыток входа за 15 минут с одного IP.
    Удачный вход счётчик не сбрасывает — 10 попыток хватает с запасом.
    """
    LIMIT, WINDOW = 10, 15 * 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path.rstrip('/').endswith('/admin/login'):
            from django.core.cache import cache
            from django.http import HttpResponse
            key = 'admin-login:' + request.META.get('REMOTE_ADDR', '')
            tries = cache.get(key, 0)
            if tries >= self.LIMIT:
                return HttpResponse('Слишком много попыток входа. Попробуйте через 15 минут.', status=429,
                                    content_type='text/plain; charset=utf-8')
            cache.set(key, tries + 1, self.WINDOW)
        return self.get_response(request)


class ApiLanguageMiddleware:
    """
    API отвечает на языке посетителя: сайт отправляет Accept-Language с выбранным
    языком. Админка и всё остальное — всегда на русском.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = 'ru'
        header = request.headers.get('Accept-Language', '')
        if request.path.startswith('/api/') and header:
            lang = _pick(header)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        if request.path.startswith('/api/'):
            response.headers.setdefault('Content-Language', lang)
        translation.deactivate()
        return response
