"""ORM for application specific database models.

Model objects are used to define the expected schema for individual database
tables and provide an object-oriented interface for executing database logic.
Each model reflects a different database and defines low-level defaults for how
the associated table/fields/records are presented by parent interfaces.
"""

from django.db import models

from apps.users.models import User

__all__ = ['AppLog', 'RequestLog']


class AppLog(models.Model):
    """An application log entry"""

    name = models.CharField(max_length=100)
    level = models.CharField(max_length=10)
    pathname = models.CharField(max_length=260)
    lineno = models.IntegerField()
    message = models.TextField()
    func = models.CharField(max_length=80, blank=True, null=True)
    sinfo = models.TextField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)


class RequestLog(models.Model):
    """Log entry for an incoming HTTP request"""

    endpoint = models.CharField(max_length=100, null=True)
    response_code = models.PositiveSmallIntegerField()
    method = models.CharField(max_length=10, null=True)
    remote_address = models.CharField(max_length=40, null=True)
    date = models.DateTimeField(auto_now=True)
    body_response = models.TextField()
    body_request = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
