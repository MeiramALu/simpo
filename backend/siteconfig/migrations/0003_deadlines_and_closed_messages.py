from django.db import migrations, models


class Migration(migrations.Migration):
    """Сроки приёма и сообщения о закрытии на трёх языках. Старое общее сообщение → русское для заявок."""
    dependencies = [('siteconfig', '0002_rolegrant')]

    operations = [
        migrations.RenameField('sitesettings', 'closed_message', 'registration_closed_ru'),
        migrations.AlterField('sitesettings', 'registration_closed_ru',
                              models.TextField('Сообщение, когда приём заявок закрыт (рус)', blank=True)),
        migrations.AddField('sitesettings', 'registration_closed_kk', models.TextField('…(каз)', blank=True)),
        migrations.AddField('sitesettings', 'registration_closed_en', models.TextField(
            '…(англ)', blank=True, help_text='Пусто — стандартный текст на языке посетителя, '
                                            'например «Приём заявок на участие завершён 15 октября 2026.»')),
        migrations.AddField('sitesettings', 'registration_deadline', models.DateField(
            'Заявки принимаются до (включительно)', null=True, blank=True,
            help_text='Пока срок не наступил, над формой написано «Заявки принимаются до …». '
                      'На следующий день приём закроется сам. Пусто — без срока.')),
        migrations.AlterField('sitesettings', 'registration_open', models.BooleanField(
            'Приём заявок на участие открыт', default=True,
            help_text='Снимите галочку, чтобы закрыть приём сразу. Вместо формы на сайте появится сообщение.')),
        migrations.AddField('sitesettings', 'papers_deadline', models.DateField(
            'Статьи принимаются до (включительно)', null=True, blank=True,
            help_text='Срок виден в личном кабинете; на следующий день приём закроется сам. '
                      'Доработку уже поданных статей можно загружать и после срока.')),
        migrations.AddField('sitesettings', 'papers_closed_ru',
                            models.TextField('Сообщение, когда приём статей закрыт (рус)', blank=True)),
        migrations.AddField('sitesettings', 'papers_closed_kk', models.TextField('…(каз)', blank=True)),
        migrations.AddField('sitesettings', 'papers_closed_en', models.TextField(
            '…(англ)', blank=True, help_text='Пусто — стандартный текст на языке посетителя.')),
    ]
