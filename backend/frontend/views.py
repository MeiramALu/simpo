import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from papers.models import PublicationFee
from registrations.models import Registration
from config.i18n import current_lang, target_label
from siteconfig.models import SiteSettings, closed_message, open_until_message

SITE_DIR = Path(__file__).resolve().parent / 'site'
SITE_INDEX = Path(os.environ.get('AFGS_SITE_INDEX', SITE_DIR / 'index.html'))
ICONS = {'favicon.png': 'image/png', 'favicon.ico': 'image/x-icon', 'apple-touch-icon.png': 'image/png'}


@ensure_csrf_cookie
def index(request):
    """Отдаёт одностраничный сайт. Файл большой (картинки и PDF внутри), поэтому читаем как есть, без шаблонизатора."""
    return HttpResponse(SITE_INDEX.read_bytes(), content_type='text/html; charset=utf-8')


NEARBY_FILE = Path(__file__).resolve().parent / 'nearby.json'


def venue_map(request):
    """
    /map/?v=0&lang=ru — отдельная страница: площадка, отели, где поесть, остановки на одной карте.
    Места рядом — frontend/nearby.json (обновляет frontend/fetch_nearby.py).
    """
    import json
    from django.shortcuts import render
    venues = json.loads(NEARBY_FILE.read_text(encoding='utf-8')) if NEARBY_FILE.exists() else []
    try:
        venue = venues[int(request.GET.get('v', 0))]
    except (ValueError, IndexError):
        raise Http404
    lang = request.GET.get('lang') if request.GET.get('lang') in ('ru', 'kk', 'en') else 'en'
    title = venue.get('title', {}).get(lang) or venue.get('addr', '')
    return render(request, 'venue_map.html', {'venue': venue, 'lang': lang, 'title': title})


def icon(request, name):
    """Значки вкладки (логотип КазНУ), их создаёт build_site.py."""
    path = SITE_DIR / name
    if name not in ICONS or not path.exists():
        raise Http404
    response = FileResponse(path.open('rb'), content_type=ICONS[name])
    response['Cache-Control'] = 'public, max-age=86400'
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def meta(request):
    """
    GET /api/meta/ — состояние приёма и справочники для сайта на языке посетителя
    (язык — из заголовка Accept-Language, см. config/middleware.py).
    """
    conf = SiteSettings.load()
    lang = current_lang()
    reg_open, papers_open = conf.registration_is_open, conf.papers_is_open
    response = Response({
        'lang': lang,
        'registration': {
            'open': reg_open,
            'deadline': conf.registration_deadline,
            'deadline_text': open_until_message('registration'),
            'closed_message': '' if reg_open else closed_message('registration'),
            'days': [{'value': v, 'label': l} for v, l in Registration.Day.choices],
            'roles': [{'value': v, 'label': l} for v, l in Registration.Role.choices],
        },
        'papers': {
            'open': papers_open,
            'deadline': conf.papers_deadline,
            'deadline_text': open_until_message('papers'),
            'closed_message': '' if papers_open else closed_message('papers'),
            'max_upload_mb': settings.PAPER_MAX_UPLOAD_MB,
            'require_verified_email': conf.require_verified_email,
        },
        'publication_targets': [
            {'value': f.target, 'label': target_label(f.target), 'fee_amount': str(f.amount),
             'fee_currency': f.currency, 'is_active': f.is_active}
            for f in PublicationFee.objects.all()
        ],
        # старые ключи — для совместимости
        'languages': [c for c, _ in settings.LANGUAGES],
        'registration_open': reg_open,
        'papers_open': papers_open,
        'paper_max_upload_mb': settings.PAPER_MAX_UPLOAD_MB,
    })
    response['Cache-Control'] = 'no-store'
    return response
