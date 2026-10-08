"""
Роли сотрудников (группы Django) и их полномочия.

Группы создаются автоматически после `migrate`. Каждое право из списка ниже
выдаётся группе один раз (учёт — в RoleGrant): если потом убрать его в админке,
оно не вернётся; новые права из новых версий кода добавятся. Вернуть права к исходным:
    python manage.py setup_roles --reset

Чтобы дать сотруднику доступ: Админка → Пользователи → отметить «Сотрудник»
(is_staff) и выбрать роль в поле «Группы».
"""
from django.contrib.auth.models import Group, Permission

VIEW_USERS = ['accounts.view_user']

ROLES = {
    'Оргкомитет': {
        'description': 'Заявки на участие: просмотр, подтверждение/отклонение, выгрузка в Excel. Докладчики и программа на сайте.',
        'perms': VIEW_USERS + [
            'program.view_programday', 'program.add_programday', 'program.change_programday',
            'program.view_programslot', 'program.add_programslot', 'program.change_programslot', 'program.delete_programslot',
            'program.view_programblock', 'program.add_programblock', 'program.change_programblock', 'program.delete_programblock',
            'program.view_programentry', 'program.add_programentry', 'program.change_programentry', 'program.delete_programentry',
            'program.view_document', 'program.add_document', 'program.change_document',
            'speakers.view_speaker', 'speakers.add_speaker', 'speakers.change_speaker', 'speakers.delete_speaker',
            'speakers.view_speakergroup', 'speakers.add_speakergroup', 'speakers.change_speakergroup',
            'registrations.view_registration', 'registrations.change_registration',
            'registrations.export_registration', 'papers.view_paper',
        ],
    },
    'Редакция': {
        'description': 'Статьи: скачивание рукописей, смена статуса и комментарий автору, выгрузка.',
        'perms': VIEW_USERS + [
            'papers.view_paper', 'papers.change_paper', 'papers.export_paper', 'papers.view_publicationfee',
        ],
    },
    'Бухгалтерия': {
        'description': 'Платежи: квитанции, подтверждение оплаты, выгрузка. Просмотр взносов.',
        'perms': VIEW_USERS + [
            'payments.view_payment', 'payments.change_payment', 'payments.confirm_payment', 'payments.export_payment',
            'papers.view_paper', 'papers.view_publicationfee',
        ],
    },
    'Администратор симпозиума': {
        'description': 'Всё выше + настройки симпозиума, суммы взносов, управление сотрудниками и их ролями.',
        'perms': [
            'accounts.view_user', 'accounts.add_user', 'accounts.change_user',
            'registrations.view_registration', 'registrations.add_registration', 'registrations.change_registration',
            'registrations.delete_registration', 'registrations.export_registration',
            'papers.view_paper', 'papers.change_paper', 'papers.export_paper',
            'papers.view_publicationfee', 'papers.change_publicationfee',
            'payments.view_payment', 'payments.change_payment', 'payments.confirm_payment', 'payments.export_payment',
            'siteconfig.view_sitesettings', 'siteconfig.change_sitesettings',
            'speakers.view_speaker', 'speakers.add_speaker', 'speakers.change_speaker', 'speakers.delete_speaker',
            'speakers.view_speakergroup', 'speakers.add_speakergroup', 'speakers.change_speakergroup', 'speakers.delete_speakergroup',
            'program.view_programday', 'program.add_programday', 'program.change_programday',
            'program.view_programslot', 'program.add_programslot', 'program.change_programslot', 'program.delete_programslot',
            'program.view_programblock', 'program.add_programblock', 'program.change_programblock', 'program.delete_programblock',
            'program.view_programentry', 'program.add_programentry', 'program.change_programentry', 'program.delete_programentry',
            'program.view_document', 'program.add_document', 'program.change_document', 'program.delete_programday', 'program.delete_document',
        ],
    },
}


def _perm(code):
    app_label, codename = code.split('.')
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)


def sync_roles(reset=False):
    from .models import RoleGrant
    changed = []
    for name, role in ROLES.items():
        group, _ = Group.objects.get_or_create(name=name)
        if reset:
            group.permissions.set([_perm(c) for c in role['perms']])
            RoleGrant.objects.filter(group=name).delete()
            new_codes = role['perms']
        else:
            done = set(RoleGrant.objects.filter(group=name).values_list('perm', flat=True))
            new_codes = [c for c in role['perms'] if c not in done]
            group.permissions.add(*[_perm(c) for c in new_codes])
        RoleGrant.objects.bulk_create([RoleGrant(group=name, perm=c) for c in new_codes], ignore_conflicts=True)
        if new_codes:
            changed.append(name)
    return changed
