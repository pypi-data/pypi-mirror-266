"""Scheduled tasks executed in parallel by Celery.

Tasks are scheduled and executed in the background by Celery. They operate
asynchronously from the rest of the application and log their results in the
application database.
"""

import logging
from datetime import date
from typing import Collection

from celery import shared_task
from django.db.models import Sum

from apps.allocations.models import Allocation, Cluster
from apps.users.models import ResearchGroup
from keystone_api.plugins.slurm import get_cluster_limit, get_cluster_usage, get_slurm_account_names, set_cluster_limit

log = logging.getLogger(__name__)


@shared_task()
def update_limits() -> None:
    """Adjust TRES billing limits for all Slurm accounts on all enabled clusters"""

    log.info(f"Begin updating TRES billing hour limits for all Slurm Accounts")
    for cluster in Cluster.objects.filter(enabled=True).all():
        log.info(f"Updating TRES billing hour limits for cluster {cluster.name}")
        update_limits_for_cluster(cluster)


@shared_task()
def update_limits_for_cluster(cluster: Cluster) -> None:
    """Adjust TRES billing limits for all Slurm accounts on a given Slurm cluster

    The account `root` is automatically ignored.

    Args:
        cluster: The name of the Slurm cluster
    """

    for account_name in get_slurm_account_names(cluster.name):
        if account_name in ['root']:
            continue

        log.debug(f"Updating TRES billing hour limits for account {account_name}")
        update_limit_for_account(account_name, cluster)


@shared_task()
def update_limit_for_account(account_name: str, cluster: Cluster) -> None:
    """Update the TRES billing usage limits for an individual Slurm account, closing out any expired allocations"""

    try:
        # Check the Slurm account has a database entry
        account = ResearchGroup.objects.get(name=account_name)

    except ResearchGroup.DoesNotExist:
        #  Lock the missing user by setting their usage limit to their current usage
        log.warning(f"No existing ResearchGroup for account {account_name}, locking {account_name} on {cluster.name}")
        set_cluster_limit(account_name, cluster.name, get_cluster_usage(account_name, cluster.name))
        return

    # Base query for approved Allocations under the given account on the given cluster
    acct_alloc_query = Allocation.objects.filter(request__group=account, cluster=cluster, request__status='AP')

    # Query for allocations that have expired but do not have a final usage value
    closing_query = acct_alloc_query \
        .filter(final=None, request__expire__lte=date.today()) \
        .order_by("request__expire")

    # Query for allocations that are active, and determine their total service unit contribution
    active_sus = acct_alloc_query \
        .filter(request__active__lte=date.today(), request__expire__gt=date.today()) \
        .aggregate(Sum("awarded"))['awarded__sum'] or 0

    # Calculate the total usage to count against expiring allocations and close them
    closing_sus = closing_query.aggregate(Sum("awarded"))['awarded__sum'] or 0
    historical_usage_from_limit = get_cluster_limit(account.name, cluster.name) - active_sus - closing_sus
    current_usage = get_cluster_usage(account.name, cluster.name) - historical_usage_from_limit
    close_expired_allocations(closing_query.all(), current_usage)

    # Set the new account usage limit using the updated historical usage from expired allocations
    updated_historical_usage = acct_alloc_query.filter(request__expire__lte=date.today()).aggregate(Sum("final"))['final__sum'] or 0
    set_cluster_limit(account_name, cluster.name, limit=updated_historical_usage + active_sus)


def close_expired_allocations(closing_allocations: Collection[Allocation], current_usage: int) -> None:
    """Set the final usage for expired allocations that have not been closed out yet

    Args:
        closing_allocations: list of `Allocation` objects to set the final usage for
        current_usage: The total TRES billing hour usage to apply across all allocations being closed out
    """

    for allocation in closing_allocations:
        log.debug(f"Closing allocation {allocation.id}")
        allocation.final = min(current_usage, allocation.awarded)
        current_usage -= allocation.final
