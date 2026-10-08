from django.conf import settings
from django.db import migrations


def seed(apps, schema_editor):
    Fee = apps.get_model('papers', 'PublicationFee')
    for target, (amount, currency) in settings.PUBLICATION_FEES.items():
        Fee.objects.get_or_create(target=target, defaults={'amount': amount, 'currency': currency})


class Migration(migrations.Migration):
    dependencies = [('papers', '0002_publicationfee_alter_paper_options')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
