"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

from celery import shared_task
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from rest_framework_simplejwt.utils import aware_utcnow


@shared_task()
def flush_expired_tokens():
    """Flush expired JWT tokens from the database"""

    OutstandingToken.objects.filter(expires_at__lte=aware_utcnow()).delete()
