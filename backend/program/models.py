import os
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models

from speakers.models import tr


class ProgramDay(models.Model):
    """День программы — вкладка на странице Programme."""
    order = models.PositiveIntegerField('Порядок', default=0)
    is_published = models.BooleanField('Показывать на сайте', default=True)
    tab_ru = models.CharField('Вкладка (рус)', max_length=100, help_text='Короткая подпись вкладки: «6 ноября»')
    tab_kk = models.CharField('Вкладка (каз)', max_length=100, blank=True)
    tab_en = models.CharField('Вкладка (англ)', max_length=100, blank=True)
    date_ru = models.CharField('Дата (рус)', max_length=200, help_text='«6 ноября 2026 (пятница)»')
    date_kk = models.CharField('Дата (каз)', max_length=200, blank=True)
    date_en = models.CharField('Дата (англ)', max_length=200, blank=True)
    event_ru = models.TextField('Событие (рус)', blank=True,
                                help_text='Первая строка — название события, следующие — тема. Пусто — заголовком будет место.')
    event_kk = models.TextField('Событие (каз)', blank=True)
    event_en = models.TextField('Событие (англ)', blank=True)
    note_ru = models.TextField('Место / примечание (рус)', blank=True)
    note_kk = models.TextField('Место / примечание (каз)', blank=True)
    note_en = models.TextField('Место / примечание (англ)', blank=True)

    class Meta:
        verbose_name = 'День программы'
        verbose_name_plural = 'Программа: дни'
        ordering = ['order', 'id']

    def __str__(self):
        return self.tab_ru


class ProgramSlot(models.Model):
    """Пункт программы: время, название, зал."""
    day = models.ForeignKey(ProgramDay, on_delete=models.CASCADE, related_name='slots', verbose_name='День')
    order = models.PositiveIntegerField('Порядок', default=0, help_text='Меньше — выше. Пункты с одинаковым временем идут параллельно.')
    is_published = models.BooleanField('Показывать на сайте', default=True)
    time_ru = models.CharField('Время (рус)', max_length=100, blank=True, help_text='«10:00 – 11:30». Пусто — «время уточняется»')
    time_kk = models.CharField('Время (каз)', max_length=100, blank=True)
    time_en = models.CharField('Время (англ)', max_length=100, blank=True)
    title_ru = models.CharField('Название (рус)', max_length=500)
    title_kk = models.CharField('Название (каз)', max_length=500, blank=True)
    title_en = models.CharField('Название (англ)', max_length=500, blank=True)
    room_ru = models.CharField('Зал / место (рус)', max_length=500, blank=True)
    room_kk = models.CharField('Зал / место (каз)', max_length=500, blank=True)
    room_en = models.CharField('Зал / место (англ)', max_length=500, blank=True)

    class Meta:
        verbose_name = 'Пункт программы'
        verbose_name_plural = 'Программа: пункты'
        ordering = ['day__order', 'order', 'id']

    def __str__(self):
        return f'{self.day.tab_ru} · {self.time_ru or "—"} · {self.title_ru[:70]}'


class ProgramBlock(models.Model):
    """Группа людей внутри пункта: «Модератор», «Докладчики», «Участники»…"""
    slot = models.ForeignKey(ProgramSlot, on_delete=models.CASCADE, related_name='blocks', verbose_name='Пункт программы')
    order = models.PositiveIntegerField('Порядок', default=0)
    label_ru = models.CharField('Подпись (рус)', max_length=255, blank=True, help_text='«Модератор», «Докладчики». Можно пусто.')
    label_kk = models.CharField('Подпись (каз)', max_length=255, blank=True)
    label_en = models.CharField('Подпись (англ)', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Группа в пункте программы'
        verbose_name_plural = 'Программа: группы выступающих'
        ordering = ['slot__day__order', 'slot__order', 'order', 'id']

    def __str__(self):
        return f'{self.slot} · {self.label_ru or "выступающие"}'


class ProgramEntry(models.Model):
    """
    Строка в программе. Либо ссылка на карточку докладчика (тогда имя, должность и тема
    берутся из карточки, а строка видна только когда карточка опубликована), либо свой текст.
    """
    block = models.ForeignKey(ProgramBlock, on_delete=models.CASCADE, related_name='entries', verbose_name='Группа')
    order = models.PositiveIntegerField('Порядок', default=0)
    speaker = models.ForeignKey('speakers.Speaker', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='program_entries', verbose_name='Карточка докладчика',
                                help_text='Если выбрана — данные берутся из карточки, и строка видна только когда карточка показана на сайте.')
    name_ru = models.CharField('ФИО (рус)', max_length=255, blank=True)
    name_kk = models.CharField('ФИО (каз)', max_length=255, blank=True)
    name_en = models.CharField('ФИО (англ)', max_length=255, blank=True)
    country_ru = models.CharField('Страна / город (рус)', max_length=255, blank=True)
    country_kk = models.CharField('Страна / город (каз)', max_length=255, blank=True)
    country_en = models.CharField('Страна / город (англ)', max_length=255, blank=True)
    role_ru = models.TextField('Должность (рус)', blank=True)
    role_kk = models.TextField('Должность (каз)', blank=True)
    role_en = models.TextField('Должность (англ)', blank=True)
    topic_ru = models.CharField('Тема (рус)', max_length=500, blank=True)
    topic_kk = models.CharField('Тема (каз)', max_length=500, blank=True)
    topic_en = models.CharField('Тема (англ)', max_length=500, blank=True)
    topic_tbc = models.BooleanField('Без темы писать «Тема уточняется»', default=False)
    text_ru = models.TextField('Или просто текст (рус)', blank=True, help_text='Вместо ФИО — одной строкой.')
    text_kk = models.TextField('Или просто текст (каз)', blank=True)
    text_en = models.TextField('Или просто текст (англ)', blank=True)

    class Meta:
        verbose_name = 'Строка программы'
        verbose_name_plural = 'Программа: выступающие'
        ordering = ['block__slot__day__order', 'block__slot__order', 'block__order', 'order', 'id']

    def __str__(self):
        if self.speaker_id:
            return self.speaker.name_ru
        return self.name_ru or self.text_ru[:80] or '—'

    def as_item(self, lang):
        """Строка в формате фронта: {name, country, role, topic, tbc} или {text}; None — не показывать."""
        if self.speaker_id:
            s = self.speaker
            if not s.is_published:
                return None
            topic = tr(s, 'topic', lang)
            return {'name': tr(s, 'name', lang), 'country': tr(s, 'country', lang), 'role': tr(s, 'role', lang),
                    'topic': topic, 'tbc': self.topic_tbc and not topic}
        if getattr(self, f'text_{lang}', ''):
            return {'text': getattr(self, f'text_{lang}')}
        if not getattr(self, f'name_{lang}', '') and self.text_ru:
            return {'text': self.text_ru}
        if not (getattr(self, f'name_{lang}', '') or self.name_ru):
            return None
        topic = tr(self, 'topic', lang)
        return {'name': tr(self, 'name', lang), 'country': tr(self, 'country', lang), 'role': tr(self, 'role', lang),
                'topic': topic, 'tbc': self.topic_tbc and not topic}


def document_upload_to(instance, filename):
    return f'documents/{instance.kind}-{instance.lang}-{uuid.uuid4().hex[:8]}{os.path.splitext(filename)[1].lower()}'


class Document(models.Model):
    """
    Файлы для кнопок «Скачать программу» и «Скачать информационное письмо» — на каждом языке свой.
    Нет файла на языке сайта — отдаётся русский; нет никакого — встроенный во фронт PDF.
    """

    class Kind(models.TextChoices):
        PROGRAM = 'program', 'Программа'
        LETTER = 'letter', 'Информационное письмо'

    kind = models.CharField('Документ', max_length=10, choices=Kind.choices)
    lang = models.CharField('Язык', max_length=2, choices=[('ru', 'Русский'), ('kk', 'Қазақша'), ('en', 'English')])
    file = models.FileField('Файл', upload_to=document_upload_to, validators=[FileExtensionValidator(['pdf', 'docx', 'doc'])],
                            help_text='PDF (лучше — откроется у всех одинаково) или Word (DOCX, DOC).')
    updated_at = models.DateTimeField('Загружен', auto_now=True)

    class Meta:
        verbose_name = 'Документ для скачивания'
        verbose_name_plural = 'Документы для скачивания'
        unique_together = [('kind', 'lang')]
        ordering = ['kind', 'lang']

    def __str__(self):
        return f'{self.get_kind_display()} — {self.get_lang_display()}'
