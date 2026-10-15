import json
from pathlib import Path

from django.db import migrations

BACKEND = Path(__file__).resolve().parent.parent.parent
SEED = BACKEND / 'program' / 'seed_program_2026_10.json'
CARDS = BACKEND / 'speakers' / 'seed_2026_10.json'
LANGS = ('ru', 'kk', 'en')


def replace(apps, schema_editor):
    """
    Программа заменяется целиком новой версией (проект от 13.10.2026). Строки докладчиков связаны с карточками:
    имя, должность и тема берутся из карточки, строка видна, пока карточка показана на сайте.
    """
    Day = apps.get_model('program', 'ProgramDay')
    Slot = apps.get_model('program', 'ProgramSlot')
    Block = apps.get_model('program', 'ProgramBlock')
    Entry = apps.get_model('program', 'ProgramEntry')
    Speaker = apps.get_model('speakers', 'Speaker')

    cards = {}
    for c in json.loads(CARDS.read_text(encoding='utf-8'))['cards']:
        cards[c['key']] = Speaker.objects.filter(group__key=c['group'], name_ru=c['name_ru'], session_ru=c['session_ru'],
                                                 registration__isnull=True).select_related('group').first()

    Day.objects.all().delete()
    for di, d in enumerate(json.loads(SEED.read_text(encoding='utf-8'))):
        day = Day.objects.create(order=(di + 1) * 10, **{f'{f}_{l}': d[f][l] for f in ('tab', 'date', 'event', 'note') for l in LANGS})
        for ri, r in enumerate(d['rows']):
            slot = Slot.objects.create(day=day, order=(ri + 1) * 10,
                                       **{f'{f}_{l}': r[f][l] for f in ('time', 'title', 'room') for l in LANGS})
            for bi, b in enumerate(r['blocks']):
                block = Block.objects.create(slot=slot, order=(bi + 1) * 10, **{f'label_{l}': b['label'][l] for l in LANGS})
                for ii, it in enumerate(b['items']):
                    if 'card' in it:
                        card = cards.get(it['card'])
                        if card is None:
                            continue
                        Entry.objects.create(block=block, order=(ii + 1) * 10, speaker=card,
                                             topic_tbc=not card.topic_ru and card.group.key != 'welcome')
                    else:
                        Entry.objects.create(block=block, order=(ii + 1) * 10, **{f'text_{l}': it['text'][l] for l in LANGS})


class Migration(migrations.Migration):
    dependencies = [
        ('program', '0003_document_word_files'),
        ('speakers', '0005_speakers_2026_10'),
    ]
    operations = [migrations.RunPython(replace, migrations.RunPython.noop)]
