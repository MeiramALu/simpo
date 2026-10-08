from django.core.validators import FileExtensionValidator
from django.urls import reverse
from rest_framework import serializers

from config.i18n import target_label

from .models import ALLOWED_EXT, Paper, validate_size

FILE_VALIDATORS = [FileExtensionValidator(ALLOWED_EXT), validate_size]


class PaperSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    target_display = serializers.SerializerMethodField()
    fee_amount = serializers.SerializerMethodField()
    fee_currency = serializers.SerializerMethodField()
    is_paid = serializers.BooleanField(read_only=True)
    can_pay = serializers.BooleanField(read_only=True)
    file = serializers.FileField(write_only=True, required=True, validators=FILE_VALIDATORS)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Paper
        fields = ['id', 'title', 'authors', 'abstract', 'keywords', 'direction', 'language', 'target', 'target_display',
                  'file', 'file_url', 'original_filename', 'status', 'status_display', 'reviewer_comment',
                  'fee_amount', 'fee_currency', 'is_paid', 'can_pay', 'created_at', 'updated_at']
        read_only_fields = ['id', 'original_filename', 'status', 'reviewer_comment', 'created_at', 'updated_at']

    def get_target_display(self, obj):
        return target_label(obj.target)

    def get_fee_amount(self, obj):
        return str(obj.fee[0])

    def get_fee_currency(self, obj):
        return obj.fee[1]

    def get_file_url(self, obj):
        request = self.context.get('request')
        url = reverse('paper-file', args=[obj.pk])
        return request.build_absolute_uri(url) if request else url

    def _apply_file(self, validated):
        f = validated.get('file')
        if f:
            validated['original_filename'] = f.name[:255]

    def create(self, validated):
        self._apply_file(validated)
        return super().create(validated)

    def update(self, instance, validated):
        self._apply_file(validated)
        old_name = instance.file.name if 'file' in validated else None
        instance = super().update(instance, validated)
        if old_name and old_name != instance.file.name:
            instance.file.storage.delete(old_name)
        return instance


class PaperUpdateSerializer(PaperSerializer):
    file = serializers.FileField(write_only=True, required=False, validators=FILE_VALIDATORS)
