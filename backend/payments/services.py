import logging

from django.db import transaction
from django.utils import timezone

from accounts.emails import notify_organizers, send_localized

from .models import Payment

log = logging.getLogger(__name__)


@transaction.atomic
def mark_paid(payment_id, raw=None, external_id=''):
    """
    Идемпотентно помечает платёж оплаченным. Вызывается из вебхука провайдера,
    тестовой кассы или из админки при ручном подтверждении.
    Возвращает True, если статус действительно поменялся.
    """
    p = Payment.objects.select_for_update().select_related('paper', 'user').get(pk=payment_id)
    if p.status == Payment.Status.PAID:
        return False
    if p.paper.payments.filter(status=Payment.Status.PAID).exclude(pk=p.pk).exists():
        log.warning('Повторная оплата статьи %s платежом %s — требуется возврат', p.paper_id, p.pk)
        p.status = Payment.Status.FAILED
        p.admin_comment = (p.admin_comment + '\nСтатья уже оплачена другим платежом — оформить возврат.').strip()
        p.save(update_fields=['status', 'admin_comment', 'updated_at'])
        notify_organizers('Двойная оплата', f'Платёж {p.pk} за уже оплаченную статью #{p.paper_id}. Нужен возврат.')
        return False
    p.status = Payment.Status.PAID
    p.paid_at = timezone.now()
    if raw:
        p.raw = {**p.raw, 'paid': raw}
    if external_id:
        p.external_id = external_id
    p.save()
    # закрыть остальные незавершённые счета по этой статье
    p.paper.payments.filter(status__in=Payment.OPEN_STATUSES).exclude(pk=p.pk).update(status=Payment.Status.CANCELLED)

    u = p.user
    from speakers.models import Speaker
    hidden = Speaker.objects.filter(is_published=False, registration__email__iexact=u.email) | \
        Speaker.objects.filter(is_published=False, registration__user=u)
    cards_note = ''
    if hidden.exists():
        cards_note = ('\n\nУ этого участника есть скрытая карточка докладчика — теперь её можно показать на сайте '
                      '(Докладчики → карточка → «Показывать на сайте»).')
    transaction.on_commit(lambda: (
        send_localized('payment_paid', u.email, u.lang, name=u.full_name, amount=p.amount, currency=p.currency, title=p.paper.title),
        notify_organizers(f'Оплата получена: {p.amount} {p.currency}',
                          f'Статья #{p.paper_id} «{p.paper.title}»\nПлательщик: {u.full_name} <{u.email}>\n'
                          f'Способ: {p.provider}\nПлатёж: {p.pk}{cards_note}'),
    ))
    return True


def set_status(payment_id, status, raw=None):
    """Неуспешные исходы (failed / cancelled) — без писем."""
    p = Payment.objects.get(pk=payment_id)
    if p.status in Payment.OPEN_STATUSES:
        p.status = status
        if raw:
            p.raw = {**p.raw, status: raw}
        p.save(update_fields=['status', 'raw', 'updated_at'])
    return p
