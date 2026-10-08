from rest_framework import serializers

from config.i18n import tr
from papers.models import Paper

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    paper_title = serializers.CharField(source='paper.title', read_only=True)
    has_receipt = serializers.SerializerMethodField()
    bank_details = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id', 'paper', 'paper_title', 'amount', 'currency', 'provider', 'status', 'status_display',
                  'payment_url', 'purpose', 'has_receipt', 'bank_details', 'payer_comment', 'admin_comment',
                  'created_at', 'paid_at']
        read_only_fields = fields

    def get_has_receipt(self, obj):
        return bool(obj.receipt)

    def get_bank_details(self, obj):
        """Реквизиты — чтобы личный кабинет мог показать их снова для неоплаченного перевода."""
        if obj.provider != 'manual':
            return None
        from siteconfig.models import SiteSettings
        return SiteSettings.load().bank_details


class PaymentCreateSerializer(serializers.Serializer):
    paper = serializers.PrimaryKeyRelatedField(queryset=Paper.objects.none())
    provider = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paper'].queryset = Paper.objects.filter(user=self.context['request'].user)

    def validate_paper(self, paper):
        if paper.is_paid:
            raise serializers.ValidationError(tr('already_paid'))
        if not paper.can_pay:
            raise serializers.ValidationError(tr('not_payable'))
        return paper


class ReceiptSerializer(serializers.Serializer):
    receipt = serializers.FileField()
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate_receipt(self, f):
        if f.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(tr('file_too_big', mb=10))
        if not f.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise serializers.ValidationError(tr('receipt_types'))
        return f
