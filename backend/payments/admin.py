from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from config.admin_utils import ExportPermissionMixin, export_csv

from .models import Payment
from .services import mark_paid


@admin.register(Payment)
class PaymentAdmin(ExportPermissionMixin, admin.ModelAdmin):
    list_display = ['short_id', 'user', 'paper', 'amount', 'currency', 'provider', 'status', 'created_at', 'paid_at']
    list_filter = ['status', 'provider', 'currency']
    search_fields = ['id', 'external_id', 'user__email', 'user__full_name', 'paper__title']
    readonly_fields = ['id', 'user', 'paper', 'amount', 'currency', 'provider', 'external_id', 'payment_url',
                       'receipt_link', 'payer_comment', 'raw', 'created_at', 'updated_at', 'paid_at']
    fields = readonly_fields[:10] + ['status', 'admin_comment'] + readonly_fields[10:]
    date_hierarchy = 'created_at'
    actions = ['confirm_paid', export_csv([
        ('ID', lambda p: p.pk),
        ('Плательщик', lambda p: p.user.full_name),
        ('Email', lambda p: p.user.email),
        ('Статья', lambda p: p.paper.title),
        ('Сумма', lambda p: p.amount),
        ('Валюта', lambda p: p.currency),
        ('Способ', lambda p: p.provider),
        ('Статус', lambda p: p.get_status_display()),
        ('ID платёжной системы', lambda p: p.external_id),
        ('Создан', lambda p: timezone.localtime(p.created_at).strftime('%d.%m.%Y %H:%M')),
        ('Оплачен', lambda p: timezone.localtime(p.paid_at).strftime('%d.%m.%Y %H:%M') if p.paid_at else ''),
    ], 'payments')]

    def has_add_permission(self, request):
        return False

    @admin.display(description='ID')
    def short_id(self, obj):
        return str(obj.pk)[:8]

    @admin.display(description='Квитанция')
    def receipt_link(self, obj):
        if not obj.receipt:
            return '—'
        return format_html('<a href="{}">скачать</a>', reverse('payment-receipt', args=[obj.pk]))

    def has_confirm_permission(self, request):
        return request.user.has_perm('payments.confirm_payment')

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not self.has_confirm_permission(request):
            ro.append('status')  # менять статус оплаты может только тот, кто подтверждает оплату
        return ro

    @admin.action(description='Подтвердить оплату (с письмом плательщику)', permissions=['confirm'])
    def confirm_paid(self, request, queryset):
        n = sum(mark_paid(p.pk, raw={'confirmed_by': request.user.email}) for p in queryset)
        self.message_user(request, f'Подтверждено платежей: {n}', messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        # «Оплачено», выставленное руками, проводим через mark_paid, чтобы ушли письма
        if change and 'status' in form.changed_data and obj.status == Payment.Status.PAID:
            obj.status = form.initial['status']
            super().save_model(request, obj, form, change)
            mark_paid(obj.pk, raw={'confirmed_by': request.user.email})
        else:
            super().save_model(request, obj, form, change)
