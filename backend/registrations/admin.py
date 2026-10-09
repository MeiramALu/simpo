from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from accounts.emails import send_localized
from config.admin_utils import ExportPermissionMixin, export_csv
from speakers.services import create_draft_card, hide_cards

from .models import Registration

STATUS_TXT = {
    'ru': dict(Registration.Status.choices),
    'kk': {'new': 'жаңа', 'confirmed': 'расталды', 'waitlist': 'күту тізімі', 'rejected': 'қабылданбады', 'cancelled': 'бас тартылды'},
    'en': {'new': 'new', 'confirmed': 'confirmed', 'waitlist': 'waiting list', 'rejected': 'declined', 'cancelled': 'cancelled'},
}


def notify_status(r):
    lang = r.lang if r.lang in STATUS_TXT else 'ru'
    send_localized('registration_status', r.email, lang, name=r.full_name,
                   status=STATUS_TXT[lang][r.status], comment=r.admin_comment)


def after_status_change(request, r):
    """
    Письмо участнику + карточка на сайте:
    подтверждён докладчик → черновик карточки (скрытый); отклонён/отменён → его карточки скрываются.
    Возвращает (создано_черновиков, скрыто_карточек).
    """
    notify_status(r)
    created = hidden = 0
    if (r.status == Registration.Status.CONFIRMED and r.role == Registration.Role.SPEAKER
            and request.user.has_perm('speakers.add_speaker')):
        created = int(create_draft_card(r)[1])
    if r.status in (Registration.Status.REJECTED, Registration.Status.CANCELLED):
        hidden = hide_cards(r)
    return created, hidden


def report_cards(modeladmin, request, created, hidden):
    if created:
        modeladmin.message_user(request, f'Создано черновиков карточек докладчиков: {created}. Они пока НЕ видны на сайте — '
                                         f'откройте «Докладчики», группа «Черновики из заявок».', messages.INFO)
    if hidden:
        modeladmin.message_user(request, f'Скрыто карточек на сайте: {hidden}.', messages.WARNING)


def _set_status(new_status, label):
    def action(modeladmin, request, queryset):
        n = created = hidden = 0
        for r in queryset.exclude(status=new_status):
            r.status = new_status
            r.save(update_fields=['status', 'updated_at'])
            c, h = after_status_change(request, r)
            created, hidden, n = created + c, hidden + h, n + 1
        modeladmin.message_user(request, f'{label}: {n}', messages.SUCCESS)
        report_cards(modeladmin, request, created, hidden)
    action.short_description = f'{label} (с письмом участнику)'
    action.__name__ = f'set_{new_status}'
    action.allowed_permissions = ('change',)
    return action


@admin.register(Registration)
class RegistrationAdmin(ExportPermissionMixin, admin.ModelAdmin):
    list_display = ['full_name', 'organization', 'country', 'email', 'day', 'role', 'status', 'site_card', 'created_at']
    list_filter = ['status', 'day', 'role', 'lang', 'country', 'direction']
    search_fields = ['full_name', 'organization', 'email', 'phone', 'topic']
    readonly_fields = ['user', 'lang', 'site_card_links', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    fieldsets = (
        ('Участник', {'fields': ('full_name', 'organization', 'country', 'email', 'phone', 'user', 'lang')}),
        ('Участие', {'fields': ('day', 'role', 'direction', 'topic', 'note')}),
        ('Оргкомитет', {'fields': ('status', 'admin_comment', 'internal_note', 'site_card_links', 'created_at', 'updated_at')}),
    )
    actions = [
        _set_status(Registration.Status.CONFIRMED, 'Подтвердить'),
        _set_status(Registration.Status.WAITLIST, 'В лист ожидания'),
        _set_status(Registration.Status.REJECTED, 'Отклонить'),
        'make_speaker_cards',
        export_csv([
            ('ID', lambda r: r.pk),
            ('ФИО', lambda r: r.full_name),
            ('Организация', lambda r: r.organization),
            ('Страна', lambda r: r.country),
            ('Email', lambda r: r.email),
            ('Телефон', lambda r: r.phone),
            ('День', lambda r: r.get_day_display()),
            ('Формат', lambda r: r.get_role_display()),
            ('Направление', lambda r: r.direction),
            ('Тема', lambda r: r.topic),
            ('Комментарий', lambda r: r.note),
            ('Статус', lambda r: r.get_status_display()),
            ('Язык', lambda r: r.lang),
            ('Подана', lambda r: timezone.localtime(r.created_at).strftime('%d.%m.%Y %H:%M')),
        ], 'registrations'),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('speaker_cards__group')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and 'status' in form.changed_data:
            report_cards(self, request, *after_status_change(request, obj))

    # --- карточка докладчика на сайте ---
    def has_speaker_card_permission(self, request):
        return request.user.has_perm('speakers.add_speaker')

    @admin.action(description='Создать черновик карточки докладчика для сайта', permissions=['speaker_card'])
    def make_speaker_cards(self, request, queryset):
        ok = queryset.filter(role=Registration.Role.SPEAKER, status=Registration.Status.CONFIRMED)
        created = sum(create_draft_card(r)[1] for r in ok)
        skipped = queryset.count() - ok.count()
        report_cards(self, request, created, 0)
        if not created:
            self.message_user(request, 'Новых черновиков нет: у выбранных докладчиков карточки уже есть.', messages.INFO)
        if skipped:
            self.message_user(request, f'Пропущено {skipped}: карточка делается только для подтверждённых докладчиков.',
                              messages.WARNING)

    @staticmethod
    def _card_state(card):
        if not card.is_published:
            return 'скрыта'
        if not card.group.is_published:
            return 'скрыта (группа скрыта)'
        return 'на сайте'

    @admin.display(description='Карточка на сайте')
    def site_card(self, obj):
        cards = list(obj.speaker_cards.all())
        if not cards:
            return '—'
        return format_html_join(', ', '<a href="{}">{}</a>', (
            (reverse('admin:speakers_speaker_change', args=[c.pk]), self._card_state(c)) for c in cards))

    @admin.display(description='Карточка докладчика')
    def site_card_links(self, obj):
        cards = list(obj.speaker_cards.all()) if obj.pk else []
        if not cards:
            if obj.role == Registration.Role.SPEAKER:
                return 'Нет. Появится черновик, когда заявку подтвердят (или действие «Создать черновик карточки…»).'
            return 'Не нужна: формат участия — слушатель.'
        return format_html_join(mark_safe('<br>'), '<a href="{}">{}</a> — {}, группа «{}»', (
            (reverse('admin:speakers_speaker_change', args=[c.pk]), c.name_ru, self._card_state(c), c.group.title_ru)
            for c in cards))
