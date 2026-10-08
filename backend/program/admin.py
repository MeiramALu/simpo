from django.contrib import admin
from django.utils.html import format_html

from speakers.admin import SpeakerAdmin

from .models import Document, ProgramBlock, ProgramDay, ProgramEntry, ProgramSlot

LANG_SETS = (('Русский', 'ru'), ('Қазақша', 'kk'), ('English', 'en'))


def lang_fieldsets(*fields, head=None):
    sets = [(None, {'fields': head})] if head else []
    for title, lang in LANG_SETS:
        opts = {'fields': tuple(f'{f}_{lang}' for f in fields)}
        if lang != 'ru':
            opts['description'] = 'Пустые поля на сайте заменяются русским вариантом.'
            opts['classes'] = ('collapse',)
        sets.append((title, opts))
    return tuple(sets)


class SlotInline(admin.TabularInline):
    model = ProgramSlot
    fields = ('order', 'time_ru', 'title_ru', 'room_ru', 'is_published')
    extra = 0
    show_change_link = True


@admin.register(ProgramDay)
class ProgramDayAdmin(admin.ModelAdmin):
    list_display = ['tab_ru', 'date_ru', 'order', 'is_published']
    list_editable = ['order', 'is_published']
    fieldsets = lang_fieldsets('tab', 'date', 'event', 'note', head=('order', 'is_published'))
    inlines = [SlotInline]


class BlockInline(admin.TabularInline):
    model = ProgramBlock
    fields = ('order', 'label_ru', 'label_kk', 'label_en', 'people')
    readonly_fields = ('people',)
    extra = 0
    show_change_link = True

    @admin.display(description='Выступающие')
    def people(self, obj):
        return ', '.join(str(e) for e in obj.entries.all()) if obj.pk else '—'


@admin.register(ProgramSlot)
class ProgramSlotAdmin(admin.ModelAdmin):
    list_display = ['title_ru', 'day', 'time_ru', 'room_ru', 'order', 'is_published']
    list_editable = ['order', 'is_published']
    list_filter = ['day']
    search_fields = ['title_ru', 'title_en', 'title_kk', 'room_ru']
    fieldsets = lang_fieldsets('time', 'title', 'room', head=('day', 'order', 'is_published'))
    inlines = [BlockInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('day')


class EntryInline(admin.TabularInline):
    model = ProgramEntry
    fields = ('order', 'speaker', 'name_ru', 'role_ru', 'topic_ru', 'topic_tbc', 'text_ru', 'shown')
    readonly_fields = ('shown',)
    autocomplete_fields = ('speaker',)
    extra = 1
    show_change_link = True

    @admin.display(description='На сайте')
    def shown(self, obj):
        if not obj.pk:
            return ''
        if obj.speaker_id and not obj.speaker.is_published:
            return format_html('<span style="color:#b26a00">скрыто: карточка не показана</span>')
        return '✓'


@admin.register(ProgramBlock)
class ProgramBlockAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    list_filter = ['slot__day']
    search_fields = ['label_ru', 'slot__title_ru', 'slot__time_ru', 'slot__day__tab_ru']
    fields = ('slot', 'order', 'label_ru', 'label_kk', 'label_en')
    autocomplete_fields = ('slot',)
    inlines = [EntryInline]


@admin.register(ProgramEntry)
class ProgramEntryAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'block', 'speaker', 'order']
    list_filter = ['block__slot__day']
    search_fields = ['name_ru', 'name_en', 'text_ru', 'speaker__name_ru', 'block__slot__title_ru']
    autocomplete_fields = ('block', 'speaker')
    fieldsets = ((None, {'fields': ('block', 'order', 'speaker', 'topic_tbc'),
                         'description': 'Выберите карточку докладчика — тогда остальные поля не нужны: имя, должность и тема '
                                        'берутся из карточки, а строка появится в программе, когда карточку покажут на сайте.'}),
                 ) + lang_fieldsets('name', 'country', 'role', 'topic', 'text')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['kind', 'lang', 'file', 'updated_at']
    list_filter = ['kind', 'lang']


# В карточке докладчика: в каких пунктах программы он выступает
class SpeakerProgramInline(admin.TabularInline):
    model = ProgramEntry
    fk_name = 'speaker'
    fields = ('block', 'order', 'topic_tbc')
    autocomplete_fields = ('block',)
    extra = 0
    verbose_name = 'Выступление в программе'
    verbose_name_plural = 'Выступления в программе (строка появится в программе, когда карточка показана на сайте)'


SpeakerAdmin.inlines = [*getattr(SpeakerAdmin, 'inlines', []), SpeakerProgramInline]
