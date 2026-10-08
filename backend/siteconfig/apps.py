from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _create_roles(sender, **kwargs):
    from .roles import sync_roles
    sync_roles()


class SiteconfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'siteconfig'
    verbose_name = 'Настройки'

    def ready(self):
        # права остальных приложений к этому моменту уже созданы:
        # siteconfig стоит в INSTALLED_APPS после них
        post_migrate.connect(_create_roles, sender=self)
