from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from config.i18n import tr

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'organization', 'country', 'phone', 'lang',
                  'email_verified', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'email', 'email_verified', 'is_staff', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'organization', 'country', 'phone', 'lang']

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(tr('email_taken'))
        return value

    def validate(self, attrs):
        validate_password(attrs['password'], User(email=attrs.get('email'), full_name=attrs.get('full_name', '')))
        return attrs

    def create(self, validated):
        return User.objects.create_user(**validated)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        user = authenticate(self.context.get('request'), email=attrs['email'].strip().lower(), password=attrs['password'])
        if not user:
            raise serializers.ValidationError(tr('bad_credentials'))
        if not user.is_active:
            raise serializers.ValidationError(tr('inactive'))
        attrs['user'] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(tr('bad_old_password'))
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UidTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class PasswordResetConfirmSerializer(UidTokenSerializer):
    new_password = serializers.CharField()
