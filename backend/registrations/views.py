from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.emails import notify_organizers, send_localized
from config.i18n import tr
from siteconfig.models import SiteSettings, closed_message
from speakers.services import hide_cards

from .models import Registration
from .serializers import RegistrationSerializer, RegistrationUpdateSerializer

DAY_TXT = {
    'ru': {'6': '6 ноября', '7': '7 ноября', 'both': 'оба дня'},
    'kk': {'6': '6 қараша', '7': '7 қараша', 'both': 'екі күн'},
    'en': {'6': '6 November', '7': '7 November', 'both': 'both days'},
}
ROLE_TXT = {
    'ru': {'listener': 'слушатель', 'speaker': 'докладчик'},
    'kk': {'listener': 'тыңдаушы', 'speaker': 'баяндамашы'},
    'en': {'listener': 'attendee', 'speaker': 'speaker'},
}


def own_registrations(user):
    q = Q(user=user)
    if user.email_verified:
        q |= Q(email__iexact=user.email)
    return Registration.objects.filter(q)


def organizers_summary(r, prefix='Новая заявка'):
    return (f'{prefix} #{r.pk}\n\nФИО: {r.full_name}\nОрганизация: {r.organization}\nСтрана: {r.country}\n'
            f'Email: {r.email}\nТелефон: {r.phone}\nДень: {r.get_day_display()}\nФормат: {r.get_role_display()}\n'
            f'Направление: {r.direction}\nТема: {r.topic}\nКомментарий: {r.note}\nЯзык: {r.lang}')


class RegistrationListCreateView(generics.ListCreateAPIView):
    """
    POST /api/registrations/ — подать заявку (можно без аккаунта, как на текущем фронте).
    GET  /api/registrations/ — мои заявки (нужен вход).
    """
    serializer_class = RegistrationSerializer

    def get_permissions(self):
        return [AllowAny()] if self.request.method == 'POST' else [IsAuthenticated()]

    def get_throttles(self):
        if self.request.method == 'POST':
            self.throttle_scope = 'registration'
            return [ScopedRateThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        return own_registrations(self.request.user)

    def create(self, request, *args, **kwargs):
        if not SiteSettings.load().registration_is_open:
            return Response({'detail': closed_message('registration', request.data.get('lang'))},
                            status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        r = serializer.save(user=user)
        lang = r.lang
        send_localized('registration_received', r.email, lang, name=r.full_name,
                       day=DAY_TXT[lang][r.day], role=ROLE_TXT[lang][r.role])
        notify_organizers(f'Новая заявка: {r.full_name}', organizers_summary(r))


class RegistrationDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/registrations/<id>/ — просмотр и правка своей заявки."""
    serializer_class = RegistrationUpdateSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        return own_registrations(self.request.user)

    def update(self, request, *args, **kwargs):
        r = self.get_object()
        if not r.is_active:
            return Response({'detail': tr('reg_locked')}, status=status.HTTP_400_BAD_REQUEST)
        response = super().update(request, *args, partial=True)
        r.refresh_from_db()
        notify_organizers(f'Заявка изменена: {r.full_name}', organizers_summary(r, 'Участник изменил заявку'))
        return response


class RegistrationCancelView(APIView):
    """POST /api/registrations/<id>/cancel/"""
    def post(self, request, pk):
        r = own_registrations(request.user).filter(pk=pk).first()
        if not r:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not r.is_active:
            return Response({'detail': tr('reg_inactive')}, status=status.HTTP_400_BAD_REQUEST)
        r.status = Registration.Status.CANCELLED
        r.save(update_fields=['status', 'updated_at'])
        hide_cards(r)
        notify_organizers(f'Заявка отменена: {r.full_name}', organizers_summary(r, 'Участник отменил заявку'))
        return Response(RegistrationSerializer(r).data)
