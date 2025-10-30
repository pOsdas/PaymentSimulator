from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from app.models import Invoice, Payment, UserBalance
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()


class BillingError(Exception):
    pass


def ensure_user_balance(user: User) -> UserBalance:
    ub, created = UserBalance.objects.get_or_create(user=user)
    return ub


@transaction.atomic
def reserve_funds(invoice: Invoice) -> bool:
    user = invoice.user
    balance = ensure_user_balance(user)

    amount = invoice.amount
    balance = UserBalance.objects.select_for_update().get(pk=balance.pk)
    success = balance.reserve(amount)
    if success:
        invoice.status = Invoice.STATUS_RESERVED
        invoice.save(update_fields=["status", "updated_at"])
        return True
    else:
        invoice.status = Invoice.STATUS_FAILED
        invoice.save(update_fields=["status", "updated_at"])
        return False


@transaction.atomic
def complete_payment(payment: Payment) -> bool:
    invoice = payment.invoice
    user = invoice.user
    balance = ensure_user_balance(user)
    balance = UserBalance.objects.select_for_update().get(pk=balance.pk)

    amount = payment.amount
    ok = balance.debit_reserved(amount)
    if not ok:
        raise BillingError("Не удается списать зарезервированные средства (недостаточно зарезервировано)")

    payment.status = Payment.STATUS_SUCCESS
    payment.provider_transaction_id = payment.provider_transaction_id or ""
    payment.save(update_fields=["status", "provider_transaction_id", "updated_at"])

    invoice.status = Invoice.STATUS_COMPLETED
    invoice.save(update_fields=["status", "updated_at"])
    return True


@transaction.atomic
def compensate_payment(payment: Payment, reason: str = ""):
    invoice = payment.invoice
    user = invoice.user
    balance = ensure_user_balance(user)
    balance = UserBalance.objects.select_for_update().get(pk=balance.pk)

    amount = payment.amount
    if balance.reserved >= amount:
        balance.release(amount)
    else:
        balance.credit(amount)

    payment.status = Payment.STATUS_FAILED
    payment.last_error = reason or payment.last_error
    payment.save(update_fields=["status", "last_error", "updated_at"])

    invoice.status = Invoice.STATUS_FAILED
    invoice.save(update_fields=["status", "updated_at"])


@transaction.atomic
def refund_payment(payment: Payment) -> bool:
    if payment.status != Payment.STATUS_SUCCESS:
        return False

    invoice = payment.invoice
    user = invoice.user
    balance = ensure_user_balance(user)
    balance = UserBalance.objects.select_for_update().get(pk=balance.pk)

    amount = payment.amount
    balance.credit(amount)

    payment.status = Payment.STATUS_REFUNDED
    payment.save(update_fields=["status", "updated_at"])

    invoice.status = Invoice.STATUS_REFUNDED
    invoice.save(update_fields=["status", "updated_at"])
    return True






