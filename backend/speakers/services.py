"""
Связь «заявка на участие → карточка на странице Speakers».

Подтверждённый докладчик НЕ появляется на сайте сам: из заявки создаётся
черновик карточки в скрытой группе «Черновики из заявок». Оргкомитет
переносит его в нужную группу, дописывает переводы и включает «Показывать на сайте».
"""
from .models import Speaker, SpeakerGroup

DRAFT_GROUP_KEY = 'drafts'


def draft_group():
    group, _ = SpeakerGroup.objects.get_or_create(
        key=DRAFT_GROUP_KEY,
        defaults={
            'title_ru': 'Черновики из заявок', 'title_kk': 'Өтінімдерден жобалар', 'title_en': 'Drafts from applications',
            'subtitle_ru': 'Скрытая группа: перенесите карточку в нужную группу и включите «Показывать на сайте»',
            'order': 999, 'is_published': False,
        })
    return group


def create_draft_card(registration):
    """Возвращает (карточка, создана_ли). Повторно для той же заявки не создаёт."""
    existing = registration.speaker_cards.first()
    if existing:
        return existing, False
    card = Speaker.objects.create(
        group=draft_group(),
        registration=registration,
        is_published=False,
        day='7' if registration.day == '7' else '6',
        name_ru=registration.full_name,
        country_ru=registration.country,
        role_ru=registration.organization,
        topic_ru=registration.topic,
        session_ru=registration.direction,
    )
    return card, True


def hide_cards(registration):
    """Заявку отклонили или отменили — её карточки убираются с сайта (не удаляются)."""
    return registration.speaker_cards.filter(is_published=True).update(is_published=False)


# --- оплата: карточку докладчика нельзя показать, пока не оплачен взнос за его статью ---
def person_user(registration):
    """Аккаунт участника по заявке: привязанный или с тем же email."""
    from accounts.models import User
    if registration is None:
        return None
    if registration.user_id:
        return registration.user
    return User.objects.filter(email__iexact=registration.email).first()


def fee_papers(user):
    """Статьи человека в платных изданиях (кроме отклонённых и отозванных)."""
    if user is None:
        return []
    return [p for p in user.papers.exclude(status__in=('rejected', 'withdrawn')) if p.fee[0] > 0]


def payment_state(registration):
    """
    ('none', [])        — платных статей нет: достаточно одобрения оргкомитета;
    ('unpaid', [статьи]) — есть неоплаченные взносы;
    ('paid', [статьи])   — всё оплачено.
    """
    papers = fee_papers(person_user(registration))
    if not papers:
        return 'none', []
    unpaid = [p for p in papers if not p.is_paid]
    return ('unpaid', unpaid) if unpaid else ('paid', papers)


PAYMENT_LABEL = {'none': 'не требуется', 'unpaid': '⏳ не оплачен', 'paid': '✓ оплачен'}
