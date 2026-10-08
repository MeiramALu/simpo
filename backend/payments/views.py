from django.conf import settings
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.emails import notify_organizers
from config.i18n import tr
from papers.views import IsEmailVerified
from siteconfig.models import SiteSettings, closed_message

from .models import Payment
from .providers import available_providers, get_provider
from .serializers import PaymentCreateSerializer, PaymentSerializer, ReceiptSerializer
from .services import mark_paid, set_status


class ProvidersView(APIView):
    """GET /api/payments/providers/ — доступные способы оплаты."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response([{'code': p.code, 'title': p.title} for p in available_providers()])


class PaymentListCreateView(generics.ListAPIView):
    """
    GET  /api/payments/ — мои платежи
    POST /api/payments/ {paper, provider} — начать оплату взноса за статью.
         Ответ: {payment, action}, где action — ссылка на оплату или реквизиты.
    """
    serializer_class = PaymentSerializer
    permission_classes = generics.ListAPIView.permission_classes + [IsEmailVerified]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('paper')

    def post(self, request):
        if not SiteSettings.load().payments_open:
            return Response({'detail': closed_message('payments')}, status=status.HTTP_403_FORBIDDEN)
        s = PaymentCreateSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        paper = s.validated_data['paper']
        provider = get_provider(s.validated_data['provider'])
        if not provider:
            return Response({'provider': [tr('provider_unavailable')]}, status=status.HTTP_400_BAD_REQUEST)

        amount, currency = paper.fee
        with transaction.atomic():
            # повторный клик «Оплатить» не плодит счета — переиспользуем открытый
            payment = (Payment.objects.select_for_update()
                       .filter(paper=paper, provider=provider.code, status=Payment.Status.PENDING,
                               amount=amount, currency=currency).first())
            if not payment:
                payment = Payment.objects.create(user=request.user, paper=paper, amount=amount,
                                                 currency=currency, provider=provider.code)
        action = provider.start(payment, request)
        return Response({'payment': PaymentSerializer(payment).data, 'action': action}, status=status.HTTP_201_CREATED)


class PaymentDetailView(generics.RetrieveAPIView):
    """GET /api/payments/<uuid>/ — статус платежа (фронт опрашивает после возврата с кассы)."""
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class PaymentReceiptView(APIView):
    """
    POST /api/payments/<uuid>/receipt/ — загрузить квитанцию о переводе (multipart: receipt, comment).
    GET  /api/payments/<uuid>/receipt/ — скачать квитанцию (плательщик или сотрудник).
    """
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        qs = Payment.objects.all() if request.user.has_perm('payments.view_payment') else Payment.objects.filter(user=request.user)
        p = get_object_or_404(qs, pk=pk)
        if not p.receipt:
            raise Http404
        return FileResponse(p.receipt.open('rb'), as_attachment=True, filename=p.receipt.name.rsplit('/', 1)[-1])

    def post(self, request, pk):
        p = get_object_or_404(Payment, pk=pk, user=request.user)
        if p.provider != 'manual' or p.status not in Payment.OPEN_STATUSES:
            return Response({'detail': tr('no_receipt_needed')}, status=status.HTTP_400_BAD_REQUEST)
        s = ReceiptSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if p.receipt:
            p.receipt.storage.delete(p.receipt.name)
        p.receipt = s.validated_data['receipt']
        p.payer_comment = s.validated_data.get('comment', '')
        p.status = Payment.Status.REVIEW
        p.save()
        notify_organizers(f'Квитанция на проверку: {p.amount} {p.currency}',
                          f'Плательщик: {p.user.full_name} <{p.user.email}>\nСтатья #{p.paper_id} «{p.paper.title}»\n'
                          f'Платёж {p.pk}\nПроверьте и подтвердите оплату в админке.')
        return Response(PaymentSerializer(p).data)


class PaymentCancelView(APIView):
    """POST /api/payments/<uuid>/cancel/"""
    def post(self, request, pk):
        p = get_object_or_404(Payment, pk=pk, user=request.user)
        if p.status != Payment.Status.PENDING:
            return Response({'detail': tr('pay_no_cancel')}, status=status.HTTP_400_BAD_REQUEST)
        p = set_status(p.pk, Payment.Status.CANCELLED)
        return Response(PaymentSerializer(p).data)


@csrf_exempt
def webhook(request, provider):
    """POST /api/payments/webhook/<provider>/ — уведомления от платёжных систем."""
    p = get_provider(provider)
    if not p or request.method != 'POST':
        raise Http404
    return p.handle_webhook(request)


@require_http_methods(['GET', 'POST'])
def test_checkout(request, pk):
    """Фиктивная платёжная страница (только при PAYMENTS_TEST_MODE)."""
    if not settings.PAYMENTS_TEST_MODE:
        raise Http404
    payment = get_object_or_404(Payment, pk=pk, provider='test')
    if request.method == 'POST':
        if request.POST.get('result') == 'success':
            mark_paid(payment.pk, raw={'test': True}, external_id=f'TEST-{payment.pk.hex[:10]}')
            result = 'success'
        else:
            set_status(payment.pk, Payment.Status.FAILED, raw={'test': True})
            result = 'fail'
        return redirect(f'{settings.FRONTEND_URL}/#/cabinet?payment={payment.pk}&result={result}')
    return render(request, 'payments/test_checkout.html', {'payment': payment})
