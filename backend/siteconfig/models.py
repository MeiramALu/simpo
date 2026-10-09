from django.conf import settings
from django.db import models

PAPER_STATUS_CHOICES = [
    ('submitted', 'Подана'),
    ('under_review', 'На рассмотрении'),
    ('revision', 'Нужна доработка'),
    ('recommended', 'Рекомендована в журнал'),
    ('accepted', 'Принята к публикации'),
    ('published', 'Опубликована'),
]


class SiteSettings(models.Model):
    """
    Настройки симпозиума, которые оргкомитет меняет в админке без программиста.
    Запись одна (pk=1). Начальные значения берутся из .env / settings.py.
    """
    # --- приём заявок на участие ---
    registration_open = models.BooleanField(
        'Приём заявок на участие открыт', default=True,
        help_text='Снимите галочку, чтобы закрыть приём сразу. Вместо формы на сайте появится сообщение.')
    registration_deadline = models.DateField(
        'Заявки принимаются до (включительно)', null=True, blank=True,
        help_text='Пока срок не наступил, над формой написано «Заявки принимаются до …». '
                  'На следующий день приём закроется сам. Пусто — без срока.')
    registration_closed_ru = models.TextField('Сообщение, когда приём заявок закрыт (рус)', blank=True)
    registration_closed_kk = models.TextField('…(каз)', blank=True)
    registration_closed_en = models.TextField('…(англ)', blank=True,
                                              help_text='Пусто — стандартный текст на языке посетителя, '
                                                        'например «Приём заявок на участие завершён 15 октября 2026.»')
    # --- приём статей ---
    papers_open = models.BooleanField('Приём статей открыт', default=True)
    papers_deadline = models.DateField(
        'Статьи принимаются до (включительно)', null=True, blank=True,
        help_text='Срок виден в личном кабинете; на следующий день приём закроется сам. '
                  'Доработку уже поданных статей можно загружать и после срока.')
    papers_closed_ru = models.TextField('Сообщение, когда приём статей закрыт (рус)', blank=True)
    papers_closed_kk = models.TextField('…(каз)', blank=True)
    papers_closed_en = models.TextField('…(англ)', blank=True, help_text='Пусто — стандартный текст на языке посетителя.')
    # --- общее ---
    payments_open = models.BooleanField('Оплата взносов открыта', default=True)
    speaker_requires_payment = models.BooleanField(
        'Докладчик появляется на сайте только после оплаты взноса', default=True,
        help_text='Если у человека есть статья в платном издании, его карточку нельзя показать на сайте и в программе, '
                  'пока взнос не оплачен. Для бесплатного сборника достаточно одобрения оргкомитета.')
    require_verified_email = models.BooleanField(
        'Требовать подтверждённую почту', default=True,
        help_text='Подавать статьи можно только после подтверждения email.')

    # --- карта мест проведения ---
    google_map_url = models.URLField(
        'Ссылка на Google-карту с точками', max_length=500, blank=True,
        help_text='Карта из «Google Мои карты» (как сделать — в описании раздела). Кнопка «Google Карты» на сайте ведёт сюда; '
                  'пусто — на место проведения в обычных Google Картах.')

    # --- уведомления ---
    organizers_emails = models.TextField(
        'Почта оргкомитета для уведомлений', blank=True,
        help_text='Сюда приходят письма о новых заявках, статьях и оплатах. Несколько адресов — через запятую. Пусто — не присылать.')
    send_participant_emails = models.BooleanField('Отправлять письма участникам', default=True,
                                                  help_text='Подтверждение заявки, смена статуса, оплата.')

    # --- оплата ---
    payable_statuses = models.CharField(
        'Когда можно платить взнос', max_length=200, default='accepted',
        help_text='Статусы статьи, при которых у автора появляется кнопка «Оплатить».')
    manual_payment_enabled = models.BooleanField('Оплата переводом по реквизитам', default=True)
    test_payment_enabled = models.BooleanField(
        'Тестовая оплата', default=False,
        help_text='Работает только если на сервере включён PAYMENTS_TEST_MODE. На боевом сайте держите выключенной.')

    bank_recipient = models.CharField('Получатель', max_length=255, blank=True)
    bank_bin = models.CharField('БИН', max_length=20, blank=True)
    bank_iik = models.CharField('ИИК (IBAN)', max_length=34, blank=True)
    bank_name = models.CharField('Банк', max_length=255, blank=True)
    bank_bik = models.CharField('БИК (SWIFT)', max_length=20, blank=True)
    bank_kbe = models.CharField('КБе', max_length=5, blank=True)
    bank_knp = models.CharField('КНП', max_length=5, blank=True)
    bank_extra = models.TextField('Дополнительно для плательщика', blank=True,
                                  help_text='Например, реквизиты для оплаты в USD или банк-корреспондент.')

    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Настройки симпозиума'
        verbose_name_plural = 'Настройки симпозиума'

    def __str__(self):
        return 'Настройки симпозиума'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cls.objects.filter(pk=1).first()
        if obj is None:
            obj = cls.objects.create(pk=1, **cls._defaults_from_env())
        return obj

    @staticmethod
    def _defaults_from_env():
        bank = getattr(settings, 'PAYMENT_BANK_DETAILS', {})
        providers = getattr(settings, 'PAYMENT_PROVIDERS', ['manual'])
        return {
            'require_verified_email': getattr(settings, 'REQUIRE_VERIFIED_EMAIL', True),
            'organizers_emails': ', '.join(getattr(settings, 'ORGANIZERS_EMAILS', [])),
            'payable_statuses': ','.join(getattr(settings, 'PAYABLE_PAPER_STATUSES', ['accepted'])),
            'manual_payment_enabled': 'manual' in providers,
            'test_payment_enabled': 'test' in providers,
            'bank_recipient': bank.get('recipient', ''),
            'bank_bin': bank.get('bin', ''),
            'bank_iik': bank.get('iik', ''),
            'bank_name': bank.get('bank', ''),
            'bank_bik': bank.get('bik', ''),
            'bank_kbe': bank.get('kbe', ''),
            'bank_knp': bank.get('knp', ''),
        }

    # --- удобные геттеры для кода ---
    @staticmethod
    def _before(deadline):
        from django.utils import timezone
        return deadline is None or timezone.localdate() <= deadline

    @property
    def registration_is_open(self):
        return self.registration_open and self._before(self.registration_deadline)

    @property
    def papers_is_open(self):
        return self.papers_open and self._before(self.papers_deadline)

    @property
    def organizers_list(self):
        return [x.strip() for x in self.organizers_emails.replace('\n', ',').split(',') if x.strip()]

    @property
    def payable_list(self):
        return [x for x in self.payable_statuses.split(',') if x]

    @property
    def bank_details(self):
        return {
            'recipient': self.bank_recipient, 'bin': self.bank_bin, 'iik': self.bank_iik, 'bank': self.bank_name,
            'bik': self.bank_bik, 'kbe': self.bank_kbe, 'knp': self.bank_knp, 'extra': self.bank_extra,
        }


CLOSED_DEFAULT = {
    'registration': {'ru': 'Приём заявок на участие закрыт.', 'kk': 'Қатысуға өтінім қабылдау жабық.',
                     'en': 'Registration is closed.'},
    'papers': {'ru': 'Приём статей закрыт.', 'kk': 'Мақала қабылдау жабық.', 'en': 'Paper submission is closed.'},
    'payments': {'ru': 'Оплата временно недоступна.', 'kk': 'Төлем уақытша қолжетімсіз.',
                 'en': 'Payment is temporarily unavailable.'},
}


CLOSED_ON = {
    'registration': {'ru': 'Приём заявок на участие завершён {date}.', 'kk': 'Қатысуға өтінім қабылдау {date} аяқталды.',
                     'en': 'Registration closed on {date}.'},
    'papers': {'ru': 'Приём статей завершён {date}.', 'kk': 'Мақала қабылдау {date} аяқталды.',
               'en': 'Paper submission closed on {date}.'},
}
OPEN_UNTIL = {
    'registration': {'ru': 'Заявки принимаются до {date} включительно.', 'kk': 'Өтінімдер {date} қоса алғанда қабылданады.',
                     'en': 'Applications are accepted until {date} inclusive.'},
    'papers': {'ru': 'Статьи принимаются до {date} включительно.', 'kk': 'Мақалалар {date} қоса алғанда қабылданады.',
               'en': 'Papers are accepted until {date} inclusive.'},
}


def closed_message(kind, lang=None):
    """Текст для посетителя, когда приём закрыт: свой из админки или стандартный (с датой, если закрыт по сроку)."""
    from config.i18n import current_lang, date_text
    lang = lang if lang in ('ru', 'kk', 'en') else current_lang()
    s = SiteSettings.load()
    custom = getattr(s, f'{kind}_closed_{lang}', '') if kind in CLOSED_ON else ''
    if custom:
        return custom
    if kind in CLOSED_ON:
        deadline = getattr(s, f'{kind}_deadline')
        if getattr(s, f'{kind}_open') and deadline and not s._before(deadline):
            return CLOSED_ON[kind][lang].format(date=date_text(deadline, lang))
    return CLOSED_DEFAULT[kind][lang]


def open_until_message(kind, lang=None):
    """«Заявки принимаются до 15 октября 2026 включительно.» — пока срок не наступил; иначе пусто."""
    from config.i18n import current_lang, date_text
    lang = lang if lang in ('ru', 'kk', 'en') else current_lang()
    s = SiteSettings.load()
    deadline = getattr(s, f'{kind}_deadline')
    if not deadline or not getattr(s, f'{kind}_is_open'):
        return ''
    return OPEN_UNTIL[kind][lang].format(date=date_text(deadline, lang))


class RoleGrant(models.Model):
    """Служебная: какие права уже выдавались ролям автоматически (см. siteconfig/roles.py)."""
    group = models.CharField(max_length=150)
    perm = models.CharField(max_length=255)

    class Meta:
        unique_together = [('group', 'perm')]
        verbose_name = 'Выданное право роли'
        verbose_name_plural = 'Выданные права ролей'
