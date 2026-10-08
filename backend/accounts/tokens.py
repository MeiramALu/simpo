from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    key_salt = 'accounts.tokens.EmailVerificationTokenGenerator'

    def _make_hash_value(self, user, timestamp):
        # токен перестаёт работать, как только почта подтверждена или изменена
        return f'{user.pk}{user.email}{user.email_verified}{timestamp}'


email_verification_token = EmailVerificationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()


def encode_uid(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


def user_from_uid(uid):
    from .models import User
    try:
        return User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return None
