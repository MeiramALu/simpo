import os
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models

LANGS = ('ru', 'kk', 'en')
DAY_LABEL = {
    'ru': {'6': '6 ноября', '7': '7 ноября'},
    'kk': {'6': '6 қараша', '7': '7 қараша'},
    'en': {'6': '6 November', '7': '7 November'},
}


def tr(obj, field, lang):
    """Значение на нужном языке; если перевода нет — русский вариант."""
    return getattr(obj, f'{field}_{lang}', '') or getattr(obj, f'{field}_ru', '')


def photo_upload_to(instance, filename):
    return f'speakers/{uuid.uuid4().hex}{os.path.splitext(filename)[1].lower()}'


class SpeakerGroup(models.Model):
    """Раздел страницы «Докладчики» — он же вкладка-фильтр (Пленарное заседание, Панели, Модераторы…)."""
    key = models.SlugField('Код', unique=True, help_text='Латиницей, без пробелов: plenary6, panels…')
    title_ru = models.CharField('Название (рус)', max_length=255)
    title_kk = models.CharField('Название (каз)', max_length=255, blank=True)
    title_en = models.CharField('Название (англ)', max_length=255, blank=True)
    subtitle_ru = models.CharField('Подзаголовок (рус)', max_length=255, blank=True)
    subtitle_kk = models.CharField('Подзаголовок (каз)', max_length=255, blank=True)
    subtitle_en = models.CharField('Подзаголовок (англ)', max_length=255, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        verbose_name = 'Группа докладчиков'
        verbose_name_plural = 'Группы докладчиков'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title_ru


class Speaker(models.Model):
    """Карточка на странице «Докладчики». Если человек выступает в двух группах — это две карточки."""

    class Day(models.TextChoices):
        DAY6 = '6', '6 ноября'
        DAY7 = '7', '7 ноября'

    group = models.ForeignKey(SpeakerGroup, on_delete=models.PROTECT, related_name='speakers', verbose_name='Группа')
    registration = models.ForeignKey('registrations.Registration', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='speaker_cards', verbose_name='Из заявки',
                                     help_text='Заявка на участие, из которой создана карточка.')
    order = models.PositiveIntegerField('Порядок', default=0, help_text='Меньше — выше на странице.')
    is_published = models.BooleanField('Показывать на сайте', default=True)
    photo = models.ImageField('Фото', upload_to=photo_upload_to, blank=True,
                              validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
                              help_text='Квадратное, от 200×200. Без фото показываются инициалы.')
    day = models.CharField('День', max_length=1, choices=Day.choices)

    name_ru = models.CharField('ФИО (рус)', max_length=255)
    name_kk = models.CharField('ФИО (каз)', max_length=255, blank=True)
    name_en = models.CharField('ФИО (англ)', max_length=255, blank=True)
    country_ru = models.CharField('Страна / город (рус)', max_length=255, blank=True)
    country_kk = models.CharField('Страна / город (каз)', max_length=255, blank=True)
    country_en = models.CharField('Страна / город (англ)', max_length=255, blank=True)
    role_ru = models.TextField('Должность, организация (рус)', blank=True)
    role_kk = models.TextField('Должность, организация (каз)', blank=True)
    role_en = models.TextField('Должность, организация (англ)', blank=True)
    topic_ru = models.CharField('Тема доклада (рус)', max_length=500, blank=True,
                                help_text='Пусто — на сайте «Тема доклада уточняется».')
    topic_kk = models.CharField('Тема доклада (каз)', max_length=500, blank=True)
    topic_en = models.CharField('Тема доклада (англ)', max_length=500, blank=True)
    session_ru = models.CharField('Сессия (рус)', max_length=500, blank=True,
                                  help_text='Где выступает: «Пленарное заседание», «Панель 1: …»')
    session_kk = models.CharField('Сессия (каз)', max_length=500, blank=True)
    session_en = models.CharField('Сессия (англ)', max_length=500, blank=True)

    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Докладчик'
        verbose_name_plural = 'Докладчики'
        ordering = ['group__order', 'order', 'id']

    def __str__(self):
        return self.name_ru

    def as_card(self, lang, photo_url=''):
        """Формат, который ждёт spCard() во фронте."""
        topic = tr(self, 'topic', lang)
        return {
            'id': self.pk,
            'name': tr(self, 'name', lang),
            'country': tr(self, 'country', lang),
            'role': tr(self, 'role', lang),
            'topic': topic,
            'tbc': not topic,
            'where': tr(self, 'session', lang),
            'day': DAY_LABEL.get(lang, DAY_LABEL['ru']).get(self.day, ''),
            'photo': photo_url,
        }
