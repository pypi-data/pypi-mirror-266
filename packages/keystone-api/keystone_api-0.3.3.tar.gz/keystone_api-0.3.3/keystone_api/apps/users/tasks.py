"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

import ldap
from celery import shared_task
from django.conf import settings
from django_auth_ldap.backend import LDAPBackend
from tqdm import tqdm

from .models import User


def get_ldap_connection() -> ldap.ldapobject.LDAPObject:
    """Establish a new LDAP connection"""

    conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
    if settings.AUTH_LDAP_BIND_DN:
        conn.bind(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

    if settings.AUTH_LDAP_START_TLS:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        conn.start_tls_s()

    return conn


@shared_task()
def ldap_update_users(prune=False) -> None:
    """Update the user database with the latest data from LDAP

    This function performs no action if the `AUTH_LDAP_SERVER_URI` setting
    is not configured in the application settings.

    Args:
        prune: Optionally delete old LDAP accounts with usernames no longer found in LDAP
    """

    if not settings.AUTH_LDAP_SERVER_URI:
        return

    # Search LDAP for all users
    conn = get_ldap_connection()
    search = conn.search_s(settings.AUTH_LDAP_USER_SEARCH.base_dn, ldap.SCOPE_SUBTREE, '(objectClass=account)')

    # Fetch keystone usernames using the LDAP attribute map defined in settings
    ldap_username_attr = settings.AUTH_LDAP_USER_ATTR_MAP.get('username', 'uid')
    ldap_names = {uid.decode() for result in search for uid in result[1][ldap_username_attr]}

    for username in tqdm(ldap_names):
        user = LDAPBackend().populate_user(username)
        if user is not None:
            user.is_ldap_user = True
            user.save()

    if prune:
        usernames = set(User.objects.filter(is_ldap=True).values_list('username', flat=True))
        users_to_delete = usernames - ldap_names
        User.objects.filter(username__in=users_to_delete).delete()
