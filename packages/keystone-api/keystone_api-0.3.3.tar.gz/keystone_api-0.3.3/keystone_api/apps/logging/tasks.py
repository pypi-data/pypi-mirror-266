"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings

from .models import *


@shared_task()
def rotate_log_files() -> None:
    """Delete old log files"""

    if settings.LOG_RECORD_ROTATION == 0:
        return

    max_record_age = datetime.now() - timedelta(seconds=settings.LOG_RECORD_ROTATION)
    AppLog.objects.filter(time__lt=max_record_age).delete()
    RequestLog.objects.filter(time__lt=max_record_age).delete()
