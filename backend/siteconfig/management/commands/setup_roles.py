from django.core.management.base import BaseCommand

from siteconfig.roles import ROLES, sync_roles


class Command(BaseCommand):
    help = 'Создаёт роли сотрудников (группы) с полномочиями. --reset возвращает права к исходным.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='перезаписать права существующих групп')

    def handle(self, *args, reset=False, **options):
        changed = sync_roles(reset=reset)
        for name, role in ROLES.items():
            mark = 'обновлена' if name in changed else 'без изменений'
            self.stdout.write(f'{name} — {mark}: {role["description"]}')
