import csv

from django.http import HttpResponse
from django.utils import timezone


def export_csv(fields, filename):
    """
    Фабрика admin-action «Выгрузить в CSV (Excel)».
    fields — список (заголовок, функция(obj) -> значение).
    """
    def action(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        stamp = timezone.localtime().strftime('%Y%m%d-%H%M')
        response['Content-Disposition'] = f'attachment; filename="{filename}-{stamp}.csv"'
        response.write('﻿')  # BOM, чтобы Excel правильно открыл кириллицу
        w = csv.writer(response, delimiter=';')
        w.writerow([h for h, _ in fields])
        for obj in queryset:
            w.writerow([get(obj) for _, get in fields])
        return response

    action.short_description = 'Выгрузить выбранное в CSV (Excel)'
    action.__name__ = f'export_csv_{filename}'
    action.allowed_permissions = ('export',)
    return action


class ExportPermissionMixin:
    """Выгрузка в Excel доступна только с правом <app>.export_<model>."""
    def has_export_permission(self, request):
        opts = self.opts
        return request.user.has_perm(f'{opts.app_label}.export_{opts.model_name}')
