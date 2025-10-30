import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_project.settings")

app = Celery("payment_simulator")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["app.api.v1"])

