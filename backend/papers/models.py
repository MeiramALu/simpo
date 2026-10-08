import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

ALLOWED_EXT = ['doc', 'docx', 'pdf', 'rtf', 'odt']


def paper_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'papers/{instance.user_id}/{uuid.uuid4().hex}{ext}'


def validate_size(f):
    from config.i18n import tr
    limit = settings.PAPER_MAX_UPLOAD_MB * 1024 * 1024
    if f.size > limit:
        raise ValidationError(tr('file_too_big', mb=settings.PAPER_MAX_UPLOAD_MB))


class Paper(models.Model):
    """Статья участника для электронного сборника или рекомендации в журнал."""

    class Target(models.TextChoices):
        PROCEEDINGS = 'proceedings', 'Электронный сборник материалов'
        TUVA = 'tuva', '«Новые исследования Тувы» (Scopus Q1)'
        VESTNIK_PHILOSOPHY = 'vestnik_philosophy', '«Вестник КазНУ. Серия философии, культурологии и политологии»'
        VESTNIK_RELIGION = 'vestnik_religion', '«Вестник КазНУ. Серия религиоведения»'
        VESTNIK_PEDAGOGY = 'vestnik_pedagogy', '«Вестник КазНУ. Серия педагогические науки»'
        VESTNIK_PSYCHOLOGY = 'vestnik_psychology', '«Вестник КазНУ. Серия психологии и социологии»'

    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Подана'
        UNDER_REVIEW = 'under_review', 'На рассмотрении'
        REVISION = 'revision', 'Нужна доработка'
        RECOMMENDED = 'recommended', 'Рекомендована в журнал'
        ACCEPTED = 'accepted', 'Принята к публикации'
        REJECTED = 'rejected', 'Отклонена'
        PUBLISHED = 'published', 'Опубликована'
        WITHDRAWN = 'withdrawn', 'Отозвана автором'

    EDITABLE_STATUSES = (Status.SUBMITTED, Status.REVISION)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='papers', verbose_name='Автор (аккаунт)')
    title = models.CharField('Название', max_length=500)
    authors = models.CharField('Авторы', max_length=1000, help_text='Через запятую, как в статье')
    abstract = models.TextField('Аннотация')
    keywords = models.CharField('Ключевые слова', max_length=500, blank=True)
    direction = models.CharField('Научное направление', max_length=500, blank=True)
    language = models.CharField('Язык статьи', max_length=2, choices=[('ru', 'Русский'), ('kk', 'Қазақша'), ('en', 'English')], default='ru')
    target = models.CharField('Куда подаётся', max_length=30, choices=Target.choices, default=Target.PROCEEDINGS)
    file = models.FileField('Файл рукописи', upload_to=paper_upload_to,
                            validators=[FileExtensionValidator(ALLOWED_EXT), validate_size])
    original_filename = models.CharField(max_length=255, blank=True, editable=False)

    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    reviewer_comment = models.TextField('Комментарий редакции (виден автору)', blank=True)

    created_at = models.DateTimeField('Подана', auto_now_add=True)
    updated_at = models.DateTimeField('Изменена', auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']
        permissions = [('export_paper', 'Может выгружать статьи в Excel')]

    def __str__(self):
        return self.title

    @property
    def fee(self):
        """(сумма, валюта) публикационного взноса — из админки «Публикационные взносы»."""
        f = PublicationFee.objects.filter(target=self.target).first()
        if f:
            return f.amount, f.currency
        return settings.PUBLICATION_FEES.get(self.target, (0, 'KZT'))

    @property
    def is_paid(self):
        return self.payments.filter(status='paid').exists()

    @property
    def can_pay(self):
        amount, _ = self.fee
        from siteconfig.models import SiteSettings
        return amount > 0 and self.status in SiteSettings.load().payable_list and not self.is_paid


class PublicationFee(models.Model):
    """Сумма взноса и приём статей по каждому изданию — меняется в админке."""
    target = models.CharField('Издание', max_length=30, choices=Paper.Target.choices, unique=True)
    amount = models.DecimalField('Взнос', max_digits=12, decimal_places=2, default=0)
    currency = models.CharField('Валюта', max_length=3, choices=[('KZT', '₸ KZT'), ('USD', '$ USD'), ('EUR', '€ EUR')], default='KZT')
    is_active = models.BooleanField('Принимаем статьи', default=True)

    class Meta:
        verbose_name = 'Публикационный взнос'
        verbose_name_plural = 'Публикационные взносы'
        ordering = ['id']

    def __str__(self):
        return f'{self.get_target_display()}: {self.amount} {self.currency}'
