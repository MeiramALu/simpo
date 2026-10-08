from django.db.models import Prefetch
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.i18n import current_lang
from speakers.models import tr

from .models import Document, ProgramBlock, ProgramDay, ProgramEntry, ProgramSlot


@api_view(['GET'])
@permission_classes([AllowAny])
def program(request):
    """
    GET /api/program/ — программа на языке посетителя в том же формате, что встроенная во фронт:
    [{tab, date, note, event: [строки] | null, rows: [{time, title, room, blocks: [{label, items}]}]}]
    Строки с карточкой докладчика видны только когда карточка опубликована.
    """
    lang = request.GET.get('lang') or current_lang()
    lang = lang if lang in ('ru', 'kk', 'en') else 'ru'
    entries = ProgramEntry.objects.select_related('speaker').order_by('order', 'id')
    blocks = ProgramBlock.objects.order_by('order', 'id').prefetch_related(Prefetch('entries', queryset=entries))
    slots = (ProgramSlot.objects.filter(is_published=True).order_by('order', 'id')
             .prefetch_related(Prefetch('blocks', queryset=blocks)))
    days = ProgramDay.objects.filter(is_published=True).prefetch_related(Prefetch('slots', queryset=slots))

    data = []
    for d in days:
        event = [x for x in tr(d, 'event', lang).splitlines() if x.strip()]
        rows = []
        for s in d.slots.all():
            row = {'time': tr(s, 'time', lang), 'title': tr(s, 'title', lang), 'room': tr(s, 'room', lang)}
            out_blocks = []
            for b in s.blocks.all():
                items = [it for it in (e.as_item(lang) for e in b.entries.all()) if it]
                if items:
                    out_blocks.append({'label': tr(b, 'label', lang) or None, 'items': items})
            if out_blocks:
                row['blocks'] = out_blocks
            rows.append(row)
        data.append({'tab': tr(d, 'tab', lang), 'date': tr(d, 'date', lang), 'note': tr(d, 'note', lang),
                     'event': event or None, 'rows': rows})
    response = Response(data)
    response['Cache-Control'] = 'public, max-age=60'
    return response


def document(request, kind):
    """GET /api/documents/<program|letter>/?lang=ru — загруженный в админке PDF (на языке или русский)."""
    lang = request.GET.get('lang', 'ru')
    docs = {d.lang: d for d in Document.objects.filter(kind=kind)}
    doc = docs.get(lang) or docs.get('ru') or next(iter(docs.values()), None)
    if not doc or not doc.file:
        raise Http404
    name = f'Al-Farabi_Symposium_2026_{"programme" if kind == "program" else "info_letter"}_{doc.lang.upper()}.pdf'
    response = FileResponse(doc.file.open('rb'), content_type='application/pdf', as_attachment=True, filename=name)
    response['Cache-Control'] = 'no-cache'
    return response
