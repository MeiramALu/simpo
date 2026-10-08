from django.conf import settings
from django.db import models


class Registration(models.Model):
    """Заявка на участие — поля один в один с формой #regform на фронте."""

    class Day(models.TextChoices):
        DAY6 = '6', '6 ноября'
        DAY7 = '7', '7 ноября'
        BOTH = 'both', 'Оба дня'

    class Role(models.TextChoices):
        LISTENER = 'listener', 'Слушатель'
        SPEAKER = 'speaker', 'Докладчик'

    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        CONFIRMED = 'confirmed', 'Подтверждена'
        WAITLIST = 'waitlist', 'Лист ожидания'
        REJECTED = 'rejected', 'Отклонена'
        CANCELLED = 'cancelled', 'Отменена участником'

    ACTIVE_STATUSES = (Status.NEW, Status.CONFIRMED, Status.WAITLIST)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='registrations', verbose_name='Аккаунт')
    full_name = models.CharField('ФИО', max_length=255)
    organization = models.CharField('Организация', max_length=255)
    country = models.CharField('Страна', max_length=100, blank=True)
    email = models.EmailField('Email', db_index=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    day = models.CharField('День участия', max_length=4, choices=Day.choices)
    role = models.CharField('Формат участия', max_length=10, choices=Role.choices)
    direction = models.CharField('Научное направление', max_length=500, blank=True)
    topic = models.CharField('Тема доклада', max_length=500, blank=True)
    note = models.TextField('Комментарий', blank=True)
    lang = models.CharField('Язык интерфейса', max_length=2, default='ru')

    status = models.CharField('Статус', max_length=10, choices=Status.choices, default=Status.NEW, db_index=True)
    admin_comment = models.TextField('Комментарий оргкомитета (виден участнику)', blank=True)
    internal_note = models.TextField('Внутренняя заметка', blank=True)

    created_at = models.DateTimeField('Подана', auto_now_add=True)
    updated_at = models.DateTimeField('Изменена', auto_now=True)

    class Meta:
        verbose_name = 'Заявка на участие'
        verbose_name_plural = 'Заявки на участие'
        ordering = ['-created_at']
        permissions = [('export_registration', 'Может выгружать заявки в Excel')]

    def __str__(self):
        return f'{self.full_name} — {self.get_day_display()}, {self.get_role_display()}'

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES
