from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import SiteSettings


GOOGLE_MAP_HELP = (
    'Чтобы в Google Картах были видны площадки, отели, кафе и остановки рядом:<ol>'
    '<li>Откройте <a href="https://www.google.com/maps/d/" target="_blank" rel="noopener">mymaps.google.com</a> '
    '→ «Создать карту». Назовите её, например «AFGS-2026: места проведения».</li>'
    '<li>В слое «Слой без названия» нажмите «Импорт» и загрузите <a href="/map/kml/venues.kml">venues.kml</a> '
    '(площадки). Переименуйте слой в «Места проведения».</li>'
    '<li>«Добавить слой» → «Импорт» — по очереди <a href="/map/kml/hotels.kml">hotels.kml</a>, '
    '<a href="/map/kml/food.kml">food.kml</a>, <a href="/map/kml/stops.kml">stops.kml</a>. '
    'Каждому слою можно задать свой цвет (значок кисти у слоя → «Единый стиль»).</li>'
    '<li>«Поделиться» → включите «Доступ для всех, у кого есть ссылка» → скопируйте ссылку и вставьте её ниже.</li></ol>'
)


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {f: forms.Textarea(attrs={'rows': 2, 'cols': 80}) for f in (
            'registration_closed_ru', 'registration_closed_kk', 'registration_closed_en',
            'papers_closed_ru', 'papers_closed_kk', 'papers_closed_en', 'organizers_emails')}


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    readonly_fields = ['updated_at']
    fieldsets = (
        ('Приём заявок на участие', {'fields': ('registration_open', 'registration_deadline', 'registration_closed_ru',
                                                'registration_closed_kk', 'registration_closed_en')}),
        ('Приём статей', {'fields': ('papers_open', 'papers_deadline', 'papers_closed_ru', 'papers_closed_kk',
                                     'papers_closed_en', 'require_verified_email')}),
        ('Уведомления', {'fields': ('organizers_emails', 'send_participant_emails')}),
        ('Карта мест проведения в Google Картах', {'fields': ('google_map_url',), 'description': GOOGLE_MAP_HELP}),
        (None, {'fields': ('updated_at',)}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_object(self, request, object_id, from_field=None):
        # запись создаётся при первом обращении, в т.ч. по прямой ссылке
        return SiteSettings.load() if str(object_id) == '1' else None

    def changelist_view(self, request, extra_context=None):
        # запись одна — сразу открываем её
        obj = SiteSettings.load()
        return redirect(reverse('admin:siteconfig_sitesettings_change', args=[obj.pk]))
