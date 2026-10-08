import os
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


def receipt_upload_to(instance, filename):
    return f'receipts/{instance.user_id}/{instance.pk}{os.path.splitext(filename)[1].lower()}'


class Payment(models.Model):
    """Оплата публикационного взноса за статью."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        REVIEW = 'review', 'Квитанция на проверке'
        PAID = 'paid', 'Оплачено'
        FAILED = 'failed', 'Ошибка оплаты'
        CANCELLED = 'cancelled', 'Отменено'
        REFUNDED = 'refunded', 'Возврат'

    OPEN_STATUSES = (Status.PENDING, Status.REVIEW)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments', verbose_name='Плательщик')
    paper = models.ForeignKey('papers.Paper', on_delete=models.PROTECT, related_name='payments', verbose_name='Статья')
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3)
    provider = models.CharField('Способ оплаты', max_length=30)
    status = models.CharField('Статус', max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)

    external_id = models.CharField('ID у платёжной системы', max_length=255, blank=True, db_index=True)
    payment_url = models.URLField('Ссылка на оплату', max_length=1000, blank=True)
    receipt = models.FileField('Квитанция', upload_to=receipt_upload_to, blank=True,
                               validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])])
    payer_comment = models.TextField('Комментарий плательщика', blank=True)
    admin_comment = models.TextField('Комментарий бухгалтерии', blank=True)
    raw = models.JSONField('Данные от платёжной системы', default=dict, blank=True)

    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)
    paid_at = models.DateTimeField('Оплачен', null=True, blank=True)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
        permissions = [
            ('confirm_payment', 'Может подтверждать оплату'),
            ('export_payment', 'Может выгружать платежи в Excel'),
        ]
        constraints = [
            # за одну статью может быть только один успешный платёж
            models.UniqueConstraint(fields=['paper'], condition=models.Q(status='paid'), name='one_paid_payment_per_paper'),
        ]

    def __str__(self):
        return f'{self.amount} {self.currency} — {self.paper} ({self.get_status_display()})'

    @property
    def purpose(self):
        """Назначение платежа для банковского перевода."""
        # двуязычное: иностранные авторы платят через SWIFT
        return (f'Публикационный взнос / Publication fee AFGS-2026, статья / paper №{self.paper_id}, '
                f'{self.user.full_name}, счёт / invoice {str(self.pk)[:8]}')
