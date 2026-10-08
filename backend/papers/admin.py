from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from accounts.emails import send_localized
from config.admin_utils import ExportPermissionMixin, export_csv

from .models import Paper, PublicationFee

STATUS_TXT = {
    'ru': dict(Paper.Status.choices),
    'kk': {'submitted': 'жіберілді', 'under_review': 'қаралуда', 'revision': 'пысықтау қажет',
           'recommended': 'журналға ұсынылды', 'accepted': 'жариялауға қабылданды', 'rejected': 'қабылданбады',
           'published': 'жарияланды', 'withdrawn': 'автор кері алды'},
    'en': {'submitted': 'submitted', 'under_review': 'under review', 'revision': 'revision required',
           'recommended': 'recommended to a journal', 'accepted': 'accepted for publication', 'rejected': 'declined',
           'published': 'published', 'withdrawn': 'withdrawn by the author'},
}


def notify_status(p):
    u = p.user
    lang = u.lang if u.lang in STATUS_TXT else 'ru'
    comment = p.reviewer_comment
    if p.can_pay:
        amount, currency = p.fee
        comment += {'ru': f'\n\nПубликационный взнос: {amount} {currency}. Оплатить можно в личном кабинете.',
                    'kk': f'\n\nЖарияланым жарнасы: {amount} {currency}. Жеке кабинетте төлеуге болады.',
                    'en': f'\n\nPublication fee: {amount} {currency}. You can pay in your personal account.'}[lang]
    send_localized('paper_status', u.email, lang, name=u.full_name, title=p.title,
                   status=STATUS_TXT[lang][p.status], comment=comment)


@admin.register(Paper)
class PaperAdmin(ExportPermissionMixin, admin.ModelAdmin):
    list_display = ['title', 'user', 'target', 'status', 'paid', 'created_at']
    list_filter = ['status', 'target', 'language', 'direction']
    search_fields = ['title', 'authors', 'keywords', 'user__email', 'user__full_name']
    readonly_fields = ['user', 'download', 'original_filename', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Статья', {'fields': ('title', 'authors', 'abstract', 'keywords', 'direction', 'language', 'target')}),
        ('Файл', {'fields': ('download', 'original_filename', 'file')}),
        ('Рассмотрение', {'fields': ('status', 'reviewer_comment', 'user', 'created_at', 'updated_at')}),
    )
    actions = [export_csv([
        ('ID', lambda p: p.pk),
        ('Название', lambda p: p.title),
        ('Авторы', lambda p: p.authors),
        ('Email', lambda p: p.user.email),
        ('Издание', lambda p: p.get_target_display()),
        ('Направление', lambda p: p.direction),
        ('Язык', lambda p: p.language),
        ('Статус', lambda p: p.get_status_display()),
        ('Оплачено', lambda p: 'да' if p.is_paid else 'нет'),
        ('Подана', lambda p: timezone.localtime(p.created_at).strftime('%d.%m.%Y %H:%M')),
    ], 'papers')]

    @admin.display(boolean=True, description='Взнос оплачен')
    def paid(self, obj):
        return obj.is_paid

    @admin.display(description='Скачать')
    def download(self, obj):
        if not obj.pk or not obj.file:
            return '—'
        return format_html('<a href="{}">{}</a>', reverse('paper-file', args=[obj.pk]), obj.original_filename or 'файл')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'status' in form.changed_data:
            notify_status(obj)


@admin.register(PublicationFee)
class PublicationFeeAdmin(admin.ModelAdmin):
    """Суммы взносов и приём статей по изданиям. Список изданий фиксированный — добавлять и удалять нельзя."""
    list_display = ['target', 'amount', 'currency', 'is_active']
    list_editable = ['amount', 'currency', 'is_active']
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
