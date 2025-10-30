from decimal import Decimal
from rest_framework import serializers
from app.models import Invoice, Payment
from django.contrib.auth import get_user_model

User = get_user_model()


class InvoiceCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(write_only=True)
    idempotency_key = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Invoice
        fields = ("user_id", "amount", "currency", "description", "idempotency_key")
        read_only_fields = ("id",)

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Amount must be positive")
        return value

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        idempotency_key = validated_data.get("idempotency_key")
        if idempotency_key:
            existing = Invoice.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return existing

        user = User.objects.get(pk=user_id)
        invoice = Invoice.objects.create(user=user, **validated_data)
        return invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ("id", "user_id", "amount", "currency", "status", "description", "created_at", "updated_at")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id", "invoice", "amount", "provider_transaction_id", "status",
            "attempts", "last_error", "created_at", "updated_at"
        )
        read_only_fields = fields

