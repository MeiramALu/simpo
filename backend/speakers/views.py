from django.db.models import Prefetch
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import LANGS, Speaker, SpeakerGroup, tr


@api_view(['GET'])
@permission_classes([AllowAny])
def speakers(request):
    """
    GET /api/speakers/?lang=ru|kk|en — опубликованные группы с карточками докладчиков.
    [{key, title, subtitle, speakers: [{name, country, role, topic, tbc, where, day, photo}]}]
    """
    lang = request.GET.get('lang', 'ru')
    lang = lang if lang in LANGS else 'ru'
    published = Speaker.objects.filter(is_published=True).order_by('order', 'id')
    groups = (SpeakerGroup.objects.filter(is_published=True)
              .prefetch_related(Prefetch('speakers', queryset=published, to_attr='published')))

    def photo(s):
        if not s.photo:
            return ''
        # ?v= сбрасывает кэш браузера при замене фото
        return request.build_absolute_uri(reverse('speaker-photo', args=[s.pk])) + f'?v={int(s.updated_at.timestamp())}'

    data = [{
        'key': g.key,
        'title': tr(g, 'title', lang),
        'subtitle': tr(g, 'subtitle', lang),
        'speakers': [s.as_card(lang, photo(s)) for s in g.published],
    } for g in groups]
    response = Response(data)
    response['Cache-Control'] = 'public, max-age=60'
    return response


def speaker_photo(request, pk):
    # скрытые карточки (черновики) — только сотрудникам, для превью в админке
    qs = Speaker.objects.all() if request.user.has_perm('speakers.view_speaker') else Speaker.objects.filter(is_published=True)
    s = get_object_or_404(qs, pk=pk)
    if not s.photo:
        raise Http404
    response = FileResponse(s.photo.open('rb'))
    response['Cache-Control'] = 'public, max-age=86400'
    return response
