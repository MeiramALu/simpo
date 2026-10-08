import json
from pathlib import Path

from django.db import migrations

SEED = Path(__file__).resolve().parent.parent / 'seed_program.json'
LANGS = ('ru', 'kk', 'en')


def seed(apps, schema_editor):
    """
    Программа, которая была во фронте, — в базу. Люди, у которых есть карточка на странице Speakers,
    связываются с ней: имя, должность и тема дальше берутся из карточки.
    """
    Day = apps.get_model('program', 'ProgramDay')
    Slot = apps.get_model('program', 'ProgramSlot')
    Block = apps.get_model('program', 'ProgramBlock')
    Entry = apps.get_model('program', 'ProgramEntry')
    Speaker = apps.get_model('speakers', 'Speaker')
    if Day.objects.exists():
        return
    cards = list(Speaker.objects.select_related('group'))

    def find_card(name, session, moderator):
        for c in cards:
            if c.name_ru == name and c.session_ru == session and (c.group.key == 'moderators') == moderator:
                return c
        return None

    days = json.loads(SEED.read_text(encoding='utf-8'))
    for di, d in enumerate(days):
        day = Day.objects.create(order=(di + 1) * 10, **{f'{f}_{l}': d[f][l] for f in ('tab', 'date', 'event', 'note') for l in LANGS})
        for ri, r in enumerate(d['rows']):
            slot = Slot.objects.create(day=day, order=(ri + 1) * 10,
                                       **{f'{f}_{l}': r[f][l] for f in ('time', 'title', 'room') for l in LANGS})
            for bi, b in enumerate(r['blocks']):
                block = Block.objects.create(slot=slot, order=(bi + 1) * 10, **{f'label_{l}': b['label'][l] for l in LANGS})
                moderator = b['label']['ru'].lower().startswith('модератор')
                for ii, it in enumerate(b['items']):
                    fields = {f'{f}_{l}': it[f][l] for f in ('name', 'country', 'role', 'topic', 'text') if f in it for l in LANGS}
                    card = find_card(it['name']['ru'], r['title']['ru'], moderator) if 'name' in it else None
                    Entry.objects.create(block=block, order=(ii + 1) * 10, speaker=card, topic_tbc=it.get('tbc', False), **fields)


class Migration(migrations.Migration):
    dependencies = [
        ('program', '0001_initial'),
        ('speakers', '0003_speaker_registration'),
    ]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
