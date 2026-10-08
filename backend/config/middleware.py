from django.utils import translation

from .i18n import LANGS


def _pick(accept_language):
    """'en-US,en;q=0.9,ru;q=0.8' → 'en'. Неизвестный язык → английский (сайт международный)."""
    for part in accept_language.split(','):
        code = part.split(';')[0].strip().lower()[:2]
        if code in LANGS:
            return code
    return 'en'


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
