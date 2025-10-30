import uuid
from decimal import Decimal
from app.models import Payment
import logging

logger = logging.getLogger(__name__)


class ExternalPaymentError(Exception):
    pass


def _deterministic_outcome_from_uuid(u: uuid.UUID) -> bool:
    last_char = u.hex[-1]
    try:
        val = int(last_char, 16)
    except ValueError:
        val = 0
    return (val % 2) == 0


def charge(payment: Payment) -> dict:
    """Симулируем charge"""
    invoice = payment.invoice
    success = _deterministic_outcome_from_uuid(invoice.id)
    provider_txn_id = f"sim-{uuid.uuid4().hex}"

    if success:
        logger.info("Имитация поставщика: успешное выставление счета %s", invoice.id)
        return {"success": True, "provider_id": provider_txn_id, "message": "OK"}
    else:
        logger.warning("Имитация поставщика: ошибка при выставлении счета %s", invoice.id)
        return {"success": False, "provider_id": provider_txn_id, "message": "Simulated failure"}


def capture(payment: Payment) -> dict:
    """
    Симулируем capture (Если двух-этапный поток). Пока такое-же как charge
    """
    return charge(payment)

