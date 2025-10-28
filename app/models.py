from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from dotenv import load_dotenv
import os


load_dotenv(encoding="utf-8")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


class Model(models.Model):
    id: int | None


class User(AbstractUser):
    id: int | None
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
