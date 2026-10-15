import json
from pathlib import Path

from django.core.files import File
from django.db import migrations

APP = Path(__file__).resolve().parent.parent
SEED = APP / 'seed_2026_10.json'
PHOTOS = APP / 'seed_photos'
LANGS = ('ru', 'kk', 'en')


def update(apps, schema_editor):
    """
    Докладчики по документам 15.10.2026: «Приветственные слова», пленарное заседание 6 ноября и четыре панели —
    с фото. Прежние пленарные и панельные карточки удаляются (кроме созданных из заявок), группы 7 ноября
    (Конгресс идёт по отдельной программе) и «Модераторы» скрываются.
    """
    Group = apps.get_model('speakers', 'SpeakerGroup')
    Speaker = apps.get_model('speakers', 'Speaker')
    data = json.loads(SEED.read_text(encoding='utf-8'))

    groups = {}
    for g in data['groups']:
        obj, _ = Group.objects.get_or_create(key=g['key'], defaults={'title_ru': g['title']['ru']})
        for l in LANGS:
            setattr(obj, f'title_{l}', g['title'][l])
            setattr(obj, f'subtitle_{l}', g['subtitle'][l])
        obj.order, obj.is_published = g['order'], g['is_published']
        obj.show_topic = g['key'] != 'welcome'
        obj.save()
        groups[g['key']] = obj
    Group.objects.filter(key__in=('plenary7', 'moderators')).update(is_published=False)

    old = Speaker.objects.filter(group__key__in=list(groups), registration__isnull=True)
    for s in old:
        if s.photo:
            s.photo.delete(save=False)
    old.delete()

    for c in data['cards']:
        s = Speaker(group=groups[c['group']], day=c['day'], order=c['order'], is_published=True,
                    **{f'{f}_{l}': c[f'{f}_{l}'] for f in ('name', 'country', 'role', 'topic', 'session') for l in LANGS})
        if c['photo'] and (PHOTOS / c['photo']).exists():
            with (PHOTOS / c['photo']).open('rb') as fh:
                s.photo.save(c['photo'], File(fh), save=False)
        s.save()


class Migration(migrations.Migration):
    dependencies = [
        ('speakers', '0004_speakergroup_show_topic'),
    ]
    operations = [migrations.RunPython(update, migrations.RunPython.noop)]
