from django.conf import settings
from django.contrib.auth import password_validation
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from config.i18n import tr

from .emails import send_localized
from .models import User
from .serializers import (EmailSerializer, LoginSerializer, PasswordChangeSerializer,
                          PasswordResetConfirmSerializer, RegisterSerializer, UidTokenSerializer,
                          UserSerializer)
from .tokens import email_verification_token, encode_uid, password_reset_token, user_from_uid


class AuthThrottleMixin:
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


def _auth_response(user, code=status.HTTP_200_OK):
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user).data}, status=code)


def send_verification_email(request, user):
    link = request.build_absolute_uri(reverse('email-verify-link')) + f'?uid={encode_uid(user)}&token={email_verification_token.make_token(user)}'
    send_localized('verify_email', user.email, user.lang, name=user.full_name, link=link)


def mark_email_verified(user):
    user.email_verified = True
    user.save(update_fields=['email_verified'])
    # подтянуть заявки, поданные с этого email без входа в аккаунт
    from registrations.models import Registration
    Registration.objects.filter(user__isnull=True, email__iexact=user.email).update(user=user)


class RegisterView(AuthThrottleMixin, generics.CreateAPIView):
    """POST /api/auth/register/ — создание аккаунта, сразу возвращает токен."""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        send_verification_email(request, user)
        return _auth_response(user, status.HTTP_201_CREATED)


class LoginView(AuthThrottleMixin, APIView):
    """POST /api/auth/login/ {email, password} → {token, user}"""
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        return _auth_response(s.validated_data['user'])


class LogoutView(APIView):
    """POST /api/auth/logout/ — удаляет токен."""
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — профиль текущего пользователя."""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    def post(self, request):
        s = PasswordChangeSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        request.user.set_password(s.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        # старые токены больше не действуют — выдаём новый
        Token.objects.filter(user=request.user).delete()
        return _auth_response(request.user)


class PasswordResetRequestView(AuthThrottleMixin, APIView):
    """POST /api/auth/password/reset/ {email} — всегда 200, чтобы не раскрывать, есть ли такой email."""
    permission_classes = [AllowAny]

    def post(self, request):
        s = EmailSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=s.validated_data['email'], is_active=True).first()
        if user:
            link = f'{settings.FRONTEND_URL}/#/reset-password?uid={encode_uid(user)}&token={password_reset_token.make_token(user)}'
            send_localized('password_reset', user.email, user.lang, name=user.full_name, link=link)
        return Response({'detail': tr('reset_sent')})


class PasswordResetConfirmView(AuthThrottleMixin, APIView):
    """POST /api/auth/password/reset/confirm/ {uid, token, new_password}"""
    permission_classes = [AllowAny]

    def post(self, request):
        s = PasswordResetConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = user_from_uid(s.validated_data['uid'])
        if not user or not password_reset_token.check_token(user, s.validated_data['token']):
            return Response({'detail': tr('bad_link')}, status=status.HTTP_400_BAD_REQUEST)
        try:
            password_validation.validate_password(s.validated_data['new_password'], user)
        except Exception as e:
            return Response({'new_password': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(s.validated_data['new_password'])
        user.save(update_fields=['password'])
        Token.objects.filter(user=user).delete()
        if not user.email_verified:  # раз получил письмо — почта его
            mark_email_verified(user)
        return _auth_response(user)


class EmailVerifyView(APIView):
    """POST /api/auth/email/verify/ {uid, token}"""
    permission_classes = [AllowAny]

    def post(self, request):
        s = UidTokenSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = user_from_uid(s.validated_data['uid'])
        if not user or not email_verification_token.check_token(user, s.validated_data['token']):
            return Response({'detail': tr('bad_link')}, status=status.HTTP_400_BAD_REQUEST)
        mark_email_verified(user)
        return Response({'detail': tr('email_verified')})


def email_verify_link(request):
    """GET-ссылка из письма: подтверждает почту и возвращает на сайт."""
    user = user_from_uid(request.GET.get('uid', ''))
    ok = bool(user and email_verification_token.check_token(user, request.GET.get('token', '')))
    if ok:
        mark_email_verified(user)
    return redirect(f'{settings.FRONTEND_URL}/#/cabinet?email_verified={1 if ok else 0}')


class EmailResendView(AuthThrottleMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.email_verified:
            return Response({'detail': tr('already_verified')})
        send_verification_email(request, request.user)
        return Response({'detail': tr('email_sent')})
