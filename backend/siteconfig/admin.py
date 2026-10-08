from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import PAPER_STATUS_CHOICES, SiteSettings


class SiteSettingsForm(forms.ModelForm):
    payable_statuses = forms.MultipleChoiceField(
        label='Когда можно платить взнос', choices=PAPER_STATUS_CHOICES, widget=forms.CheckboxSelectMultiple,
        required=False, help_text='Статусы статьи, при которых у автора появляется кнопка «Оплатить».')

    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {f: forms.Textarea(attrs={'rows': 2, 'cols': 80}) for f in (
            'registration_closed_ru', 'registration_closed_kk', 'registration_closed_en',
            'papers_closed_ru', 'papers_closed_kk', 'papers_closed_en', 'organizers_emails', 'bank_extra')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['payable_statuses'] = self.instance.payable_list

    def clean_payable_statuses(self):
        return ','.join(self.cleaned_data['payable_statuses'])


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    readonly_fields = ['updated_at']
    fieldsets = (
        ('Приём заявок на участие', {'fields': ('registration_open', 'registration_deadline', 'registration_closed_ru',
                                                'registration_closed_kk', 'registration_closed_en')}),
        ('Приём статей', {'fields': ('papers_open', 'papers_deadline', 'papers_closed_ru', 'papers_closed_kk',
                                     'papers_closed_en', 'require_verified_email')}),
        ('Докладчики', {'fields': ('speaker_requires_payment',)}),
        ('Уведомления', {'fields': ('organizers_emails', 'send_participant_emails')}),
        ('Оплата', {'fields': ('payments_open', 'payable_statuses', 'manual_payment_enabled', 'test_payment_enabled')}),
        ('Реквизиты для перевода', {'fields': ('bank_recipient', 'bank_bin', 'bank_iik', 'bank_name', 'bank_bik',
                                               'bank_kbe', 'bank_knp', 'bank_extra')}),
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
