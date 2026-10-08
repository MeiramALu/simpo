"""
Способы оплаты.

Каждый провайдер умеет:
  * start(payment, request)   — подготовить оплату и вернуть, что показать пользователю
                                (ссылку на платёжную страницу или реквизиты);
  * handle_webhook(request)   — принять уведомление от платёжной системы и
                                вернуть HttpResponse, который она ждёт.

Чтобы подключить реальный эквайринг (Halyk ePay, FreedomPay, CloudPayments,
Kaspi и т.п.), создайте наследника BaseProvider по документации банка,
зарегистрируйте его в PROVIDERS и добавьте переключатель в SiteSettings
(siteconfig/models.py), чтобы его можно было включать из админки.
Вебхук будет доступен по адресу /api/payments/webhook/<code>/.
Главное правило: статус «оплачено» ставится ТОЛЬКО через mark_paid() после
проверки подписи уведомления, а не по редиректу пользователя.
"""
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse

from siteconfig.models import SiteSettings


class BaseProvider:
    code = ''
    title = {'ru': '', 'kk': '', 'en': ''}

    #: имя поля-переключателя в «Настройках симпозиума»
    setting_field = ''

    def is_available(self):
        return bool(self.setting_field) and getattr(SiteSettings.load(), self.setting_field, False)

    def start(self, payment, request):
        raise NotImplementedError

    def handle_webhook(self, request):
        return HttpResponse(status=404)


class ManualProvider(BaseProvider):
    """Оплата по реквизитам: участник переводит деньги и загружает квитанцию, оргкомитет подтверждает в админке."""
    code = 'manual'
    setting_field = 'manual_payment_enabled'
    title = {'ru': 'Банковский перевод по реквизитам', 'kk': 'Деректемелер бойынша банктік аударым',
             'en': 'Bank transfer'}

    def start(self, payment, request):
        return {
            'type': 'bank_transfer',
            'bank_details': SiteSettings.load().bank_details,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'purpose': payment.purpose,
            'receipt_upload_url': request.build_absolute_uri(reverse('payment-receipt', args=[payment.pk])),
        }


class TestProvider(BaseProvider):
    """Фиктивная касса для разработки и демонстрации. В продакшене выключена."""
    code = 'test'
    setting_field = 'test_payment_enabled'
    title = {'ru': 'Тестовая оплата', 'kk': 'Тестілік төлем', 'en': 'Test payment'}

    def is_available(self):
        return super().is_available() and settings.PAYMENTS_TEST_MODE

    def start(self, payment, request):
        url = request.build_absolute_uri(reverse('payment-test-checkout', args=[payment.pk]))
        payment.payment_url = url
        payment.save(update_fields=['payment_url', 'updated_at'])
        return {'type': 'redirect', 'payment_url': url}


PROVIDERS = {p.code: p for p in (ManualProvider(), TestProvider())}


def get_provider(code):
    p = PROVIDERS.get(code)
    return p if p and p.is_available() else None


def available_providers():
    return [p for p in PROVIDERS.values() if p.is_available()]
