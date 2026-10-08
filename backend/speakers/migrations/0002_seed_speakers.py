import json
from pathlib import Path

from django.db import migrations

SEED = Path(__file__).resolve().parent.parent / 'seed_speakers.json'


def seed(apps, schema_editor):
    """Докладчики и модераторы, которые были на сайте до появления админки (из программы фронта)."""
    Group = apps.get_model('speakers', 'SpeakerGroup')
    Speaker = apps.get_model('speakers', 'Speaker')
    if Group.objects.exists():
        return
    data = json.loads(SEED.read_text(encoding='utf-8'))
    groups = {}
    for i, g in enumerate(data['groups']):
        groups[g['key']] = Group.objects.create(
            key=g['key'], order=(i + 1) * 10,
            **{f'title_{l}': v for l, v in g['title'].items()},
            **{f'subtitle_{l}': v for l, v in g['subtitle'].items()},
        )
    for s in data['speakers']:
        s = dict(s)
        Speaker.objects.create(group=groups[s.pop('group')], **s)


class Migration(migrations.Migration):
    dependencies = [('speakers', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
