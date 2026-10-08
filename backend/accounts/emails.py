"""
Отправка писем участникам на их языке (ru/kk/en).

Тексты намеренно короткие и лежат прямо здесь, чтобы оргкомитету было легко их
править. Письма уходят через EMAIL_BACKEND (в разработке — в консоль).
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

log = logging.getLogger(__name__)

SIGNATURE = {
    'ru': '\n\n—\nОргкомитет Глобального симпозиума аль-Фараби – 2026\nal-farabi@kaznu.kz',
    'kk': '\n\n—\nӘл-Фараби жаһандық симпозиумы – 2026 ұйымдастыру комитеті\nal-farabi@kaznu.kz',
    'en': '\n\n—\nOrganising Committee, Al-Farabi Global Symposium 2026\nal-farabi@kaznu.kz',
}

MESSAGES = {
    'verify_email': {
        'ru': ('Подтвердите адрес почты', 'Здравствуйте, {name}!\n\nЧтобы подтвердить адрес почты, перейдите по ссылке:\n{link}'),
        'kk': ('Электрондық поштаны растаңыз', 'Сәлеметсіз бе, {name}!\n\nПоштаны растау үшін сілтемеге өтіңіз:\n{link}'),
        'en': ('Confirm your email', 'Dear {name},\n\nPlease confirm your email address by following this link:\n{link}'),
    },
    'password_reset': {
        'ru': ('Восстановление пароля', 'Здравствуйте, {name}!\n\nДля смены пароля перейдите по ссылке:\n{link}\n\nЕсли вы не запрашивали смену пароля, просто проигнорируйте письмо.'),
        'kk': ('Құпиясөзді қалпына келтіру', 'Сәлеметсіз бе, {name}!\n\nҚұпиясөзді өзгерту үшін сілтемеге өтіңіз:\n{link}\n\nЕгер сіз сұрамаған болсаңыз, хатты елемеңіз.'),
        'en': ('Password reset', 'Dear {name},\n\nTo set a new password, follow this link:\n{link}\n\nIf you did not request this, please ignore this email.'),
    },
    'registration_received': {
        'ru': ('Заявка на участие получена', 'Здравствуйте, {name}!\n\nМы получили вашу заявку на участие в Глобальном симпозиуме аль-Фараби – 2026.\nДень участия: {day}\nФормат: {role}\n\nОргкомитет свяжется с вами по электронной почте.'),
        'kk': ('Қатысуға өтінім алынды', 'Сәлеметсіз бе, {name}!\n\nӘл-Фараби жаһандық симпозиумы – 2026-ға қатысу өтініміңіз алынды.\nҚатысу күні: {day}\nФормат: {role}\n\nҰйымдастыру комитеті сізбен электрондық пошта арқылы байланысады.'),
        'en': ('Application received', 'Dear {name},\n\nWe have received your application to take part in the Al-Farabi Global Symposium 2026.\nDay of attendance: {day}\nParticipation: {role}\n\nThe organising committee will contact you by email.'),
    },
    'registration_status': {
        'ru': ('Статус заявки изменён', 'Здравствуйте, {name}!\n\nСтатус вашей заявки: {status}.\n{comment}'),
        'kk': ('Өтінім мәртебесі өзгерді', 'Сәлеметсіз бе, {name}!\n\nӨтініміңіздің мәртебесі: {status}.\n{comment}'),
        'en': ('Application status updated', 'Dear {name},\n\nYour application status: {status}.\n{comment}'),
    },
    'paper_received': {
        'ru': ('Статья получена', 'Здравствуйте, {name}!\n\nСтатья «{title}» получена и передана на рассмотрение.'),
        'kk': ('Мақала алынды', 'Сәлеметсіз бе, {name}!\n\n«{title}» мақаласы алынды және қарауға жіберілді.'),
        'en': ('Paper received', 'Dear {name},\n\nYour paper “{title}” has been received and sent for review.'),
    },
    'paper_status': {
        'ru': ('Статус статьи изменён', 'Здравствуйте, {name}!\n\nСтатус статьи «{title}»: {status}.\n{comment}'),
        'kk': ('Мақала мәртебесі өзгерді', 'Сәлеметсіз бе, {name}!\n\n«{title}» мақаласының мәртебесі: {status}.\n{comment}'),
        'en': ('Paper status updated', 'Dear {name},\n\nStatus of your paper “{title}”: {status}.\n{comment}'),
    },
    'payment_paid': {
        'ru': ('Оплата получена', 'Здравствуйте, {name}!\n\nОплата публикационного взноса {amount} {currency} за статью «{title}» получена. Спасибо!'),
        'kk': ('Төлем алынды', 'Сәлеметсіз бе, {name}!\n\n«{title}» мақаласы үшін {amount} {currency} жарияланым жарнасы алынды. Рахмет!'),
        'en': ('Payment received', 'Dear {name},\n\nWe have received the publication fee of {amount} {currency} for your paper “{title}”. Thank you!'),
    },
}


def send_localized(kind, to, lang='ru', **ctx):
    from siteconfig.models import SiteSettings
    # служебные письма (подтверждение почты, пароль) уходят всегда
    if kind not in ('verify_email', 'password_reset') and not SiteSettings.load().send_participant_emails:
        return
    lang = lang if lang in ('ru', 'kk', 'en') else 'ru'
    subject, body = MESSAGES[kind][lang]
    body = body.format(**ctx).rstrip() + SIGNATURE[lang]
    try:
        send_mail(f'AFGS 2026 — {subject}', body, settings.DEFAULT_FROM_EMAIL, [to])
    except Exception:  # письмо не должно ронять запрос
        log.exception('Не удалось отправить письмо %s на %s', kind, to)


def notify_organizers(subject, body):
    from siteconfig.models import SiteSettings
    to = SiteSettings.load().organizers_list
    if not to:
        return
    try:
        send_mail(f'[AFGS 2026] {subject}', body, settings.DEFAULT_FROM_EMAIL, to)
    except Exception:
        log.exception('Не удалось уведомить оргкомитет: %s', subject)
