from rest_framework import serializers

from config.i18n import tr

from .models import Registration




class RegistrationSerializer(serializers.ModelSerializer):
    """
    Принимает JSON ровно в том виде, в каком его собирает фронт (submitReg):
    name, org, country, email, phone, day, role, direction, topic, note, lang.
    """
    name = serializers.CharField(source='full_name', max_length=255)
    org = serializers.CharField(source='organization', max_length=255)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    # фронт присылает submittedAt — принимаем и игнорируем, время ставит сервер
    submittedAt = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Registration
        fields = ['id', 'name', 'org', 'country', 'email', 'phone', 'day', 'day_display', 'role', 'role_display',
                  'direction', 'topic', 'note', 'lang', 'status', 'status_display', 'admin_comment',
                  'created_at', 'updated_at', 'submittedAt']
        read_only_fields = ['id', 'status', 'admin_comment', 'created_at', 'updated_at']

    def validate_email(self, value):
        return value.strip().lower()

    def validate_lang(self, value):
        return value if value in ('ru', 'kk', 'en') else 'ru'

    def validate(self, attrs):
        attrs.pop('submittedAt', None)
        if attrs.get('role', getattr(self.instance, 'role', None)) != Registration.Role.SPEAKER:
            attrs['topic'] = ''
        email = attrs.get('email', getattr(self.instance, 'email', None))
        dup = Registration.objects.filter(email__iexact=email, status__in=Registration.ACTIVE_STATUSES)
        if self.instance:
            dup = dup.exclude(pk=self.instance.pk)
        if dup.exists():
            lang = attrs.get('lang') or getattr(self.instance, 'lang', None)
            raise serializers.ValidationError({'email': tr('reg_duplicate', lang)}, code='duplicate')
        return attrs


class RegistrationUpdateSerializer(RegistrationSerializer):
    """Участник может менять только содержательные поля, email — нет."""
    class Meta(RegistrationSerializer.Meta):
        read_only_fields = RegistrationSerializer.Meta.read_only_fields + ['email']
