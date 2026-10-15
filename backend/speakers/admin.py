from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Speaker, SpeakerGroup


@admin.register(SpeakerGroup)
class SpeakerGroupAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'key', 'speakers_count', 'order', 'is_published']
    list_editable = ['order', 'is_published']
    prepopulated_fields = {'key': ('title_en',)}
    fieldsets = (
        (None, {'fields': ('key', 'order', 'is_published', 'show_topic')}),
        ('Название вкладки', {'fields': ('title_ru', 'title_kk', 'title_en')}),
        ('Подзаголовок', {'fields': ('subtitle_ru', 'subtitle_kk', 'subtitle_en')}),
    )

    @admin.display(description='Докладчиков')
    def speakers_count(self, obj):
        return obj.speakers.count()


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'name_ru', 'country_ru', 'group', 'day', 'has_topic', 'from_application', 'order', 'is_published']
    list_display_links = ['thumb', 'name_ru']
    list_editable = ['order', 'is_published']
    list_filter = ['group', 'day', 'is_published']
    search_fields = ['name_ru', 'name_kk', 'name_en', 'role_ru', 'country_ru', 'topic_ru']
    list_per_page = 100
    save_as = True  # «Сохранить как новый» — удобно, если человек выступает ещё в одной группе
    fieldsets = (
        (None, {'fields': ('group', 'day', 'order', 'is_published', 'photo', 'photo_preview', 'application_link'),
                'description': 'Карточка из заявки сначала лежит в скрытой группе «Черновики из заявок». Чтобы показать её '
                               'на сайте: выберите группу, заполните переводы и сессию, отметьте «Показывать на сайте».'}),
        ('Русский', {'fields': ('name_ru', 'country_ru', 'role_ru', 'topic_ru', 'session_ru')}),
        ('Қазақша', {'fields': ('name_kk', 'country_kk', 'role_kk', 'topic_kk', 'session_kk'),
                     'description': 'Пустые поля на сайте заменяются русским вариантом.'}),
        ('English', {'fields': ('name_en', 'country_en', 'role_en', 'topic_en', 'session_en'),
                     'description': 'Пустые поля на сайте заменяются русским вариантом.'}),
    )
    readonly_fields = ['photo_preview', 'application_link']

    def _img(self, obj, size):
        if not obj.pk or not obj.photo:
            return '—'
        return format_html('<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:50%">',
                           reverse('speaker-photo', args=[obj.pk]), size, size)

    @admin.display(description='')
    def thumb(self, obj):
        return self._img(obj, 36)

    @admin.display(description='Текущее фото')
    def photo_preview(self, obj):
        return self._img(obj, 120)

    @admin.display(description='Из заявки')
    def application_link(self, obj):
        r = obj.registration
        if not r:
            return '—'
        return format_html('<a href="{}">{} — {}</a>', reverse('admin:registrations_registration_change', args=[r.pk]),
                           r.full_name, r.get_status_display())

    @admin.display(boolean=True, description='Из заявки')
    def from_application(self, obj):
        return obj.registration_id is not None

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('group', 'registration')

    @admin.display(boolean=True, description='Тема')
    def has_topic(self, obj):
        return bool(obj.topic_ru)
