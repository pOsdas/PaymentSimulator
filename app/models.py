from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.db import models
from django.utils import timezone
from dotenv import load_dotenv
import os
import uuid


load_dotenv(encoding="utf-8")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


class Model(models.Model):
    id: int | None


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        ('administrator', 'Администратор'),
        ('user', 'Пользователь'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=False,
        null=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="balance")
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    reserved = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Баланс пользователя"
        verbose_name_plural = "Баланс пользователей"

    def available(self) -> Decimal:
        return self.balance - self.reserved

    def reserve(self, amount: Decimal) -> bool:
        if amount <= 0:
            return False
        if self.available() < amount:
            return False
        self.reserved += amount
        self.save(update_fields=["reserved", "updated_at"])
        return True

    def debit_reserved(self, amount: Decimal) -> bool:
        if amount <= 0:
            return False
        if self.reserved < amount:
            return False
        self.reserved -= amount
        self.balance = max(Decimal("0.00"), self.balance - amount)
        self.save(update_fields=["reserved", "balance", "updated_at"])
        return True

    def credit(self, amount: Decimal):
        if amount <= 0:
            return
        self.balance += amount
        self.save(update_fields=["balance", "updated_at"])

    def release(self, amount: Decimal) -> bool:
        if amount <= 0:
            return False
        if self.reserved < amount:
            return False
        self.reserved -= amount
        self.save(update_fields=["reserved", "updated_at"])
        return True


class Invoice(models.Model):
    STATUS_PENDING = "pending"
    STATUS_RESERVED = "reserved"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    idempotency_key = models.CharField(max_length=128, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Счет"
        verbose_name_plural = "Счета"

    def __str__(self):
        return f"Invoice {self.id} user={self.user_id} amount={self.amount} status={self.status}"


class Payment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    provider_transaction_id = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Payment {self.id} invoice={self.invoice_id} amount={self.amount} status={self.status}"

