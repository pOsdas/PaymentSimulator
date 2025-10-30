from celery import shared_task
from django.db import transaction
from django.shortcuts import get_object_or_404
from app.models import Invoice, Payment
from app.api.payments.services import billing, payment_processor
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_invoice_task(self, invoice_id: str):
    try:
        invoice = get_object_or_404(Invoice, pk=invoice_id)
    except Exception as e:
        logger.exception("Invoice not found: %s", invoice_id)
        return

    if invoice.status in (Invoice.STATUS_COMPLETED, Invoice.STATUS_REFUNDED):
        logger.info("Invoice %s already finished with status %s", invoice_id, invoice.status)
        return

    try:
        reserved = billing.reserve_funds(invoice)
    except Exception as exc:
        logger.exception("Error reserving funds for invoice %s: %s", invoice_id, exc)
        invoice.status = Invoice.STATUS_FAILED
        invoice.save(update_fields=["status", "updated_at"])
        return

    if not reserved:
        logger.info("Not enough funds to reserve for invoice %s", invoice_id)
        return

    payment, created = Payment.objects.get_or_create(
        invoice=invoice,
        defaults={"amount": invoice.amount}
    )

    if payment.status == Payment.STATUS_SUCCESS:
        logger.info("Payment for invoice %s already success", invoice_id)
        return

    try:
        payment.attempts += 1
        payment.save(update_fields=["attempts", "updated_at"])

        result = payment_processor.charge(payment)
        payment.provider_transaction_id = result.get("provider_id")
        if result.get("success"):
            with transaction.atomic():
                billing.complete_payment(payment)
                payment.status = Payment.STATUS_SUCCESS
                payment.save(update_fields=["status", "provider_transaction_id", "updated_at"])
                logger.info("Payment success for invoice %s", invoice_id)
        else:
            reason = result.get("message", "unknown")
            payment.last_error = reason
            payment.status = Payment.STATUS_FAILED
            payment.save(update_fields=["last_error", "status", "provider_transaction_id", "updated_at"])
            billing.compensate_payment(payment, reason=reason)
            logger.info("Payment failed and compensated for invoice %s, reason: %s", invoice_id, reason)

    except Exception as exc:
        logger.exception("Exception during payment processing for invoice %s: %s", invoice_id, exc)
        try:
            raise self.retry(exc=exc)
        except Exception:
            payment.last_error = str(exc)
            payment.save(update_fields=["last_error", "updated_at"])
            billing.compensate_payment(payment, reason=str(exc))\



@shared_task(bind=True)
def refund_invoice_task(self, payment_id: str):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except Payment.DoesNotExist:
        logger.warning("Payment not found for refund: %s", payment_id)
        return

    if payment.status != Payment.STATUS_SUCCESS:
        logger.info("Payment %s not eligible for refund (status=%s)", payment_id, payment.status)
        return

    try:
        billing.refund_payment(payment)
        logger.info("Payment %s refunded", payment_id)
    except Exception:
        logger.exception("Failed to refund payment %s", payment_id)
        raise
