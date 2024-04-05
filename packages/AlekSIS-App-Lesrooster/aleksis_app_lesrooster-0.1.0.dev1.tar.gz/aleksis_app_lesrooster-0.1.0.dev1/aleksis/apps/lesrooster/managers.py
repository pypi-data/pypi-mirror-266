from django.db.models import QuerySet

from aleksis.core.managers import AlekSISBaseManagerWithoutMigrations, DateRangeQuerySetMixin


class ValidityRangeQuerySet(QuerySet, DateRangeQuerySetMixin):
    """Custom query set for validity ranges."""


class ValidityRangeManager(AlekSISBaseManagerWithoutMigrations):
    """Manager for validity ranges."""
