from graphene_django.types import DjangoObjectType
from graphene_django_cud.mutations import (
    DjangoBatchCreateMutation,
    DjangoBatchDeleteMutation,
    DjangoBatchPatchMutation,
)
from guardian.shortcuts import get_objects_for_user

from aleksis.core.schema.base import (
    DjangoFilterMixin,
    PermissionBatchDeleteMixin,
    PermissionBatchPatchMixin,
    PermissionsTypeMixin,
)

from ..models import TimeGrid


class TimeGridType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = TimeGrid
        fields = (
            "id",
            "validity_range",
            "group",
        )
        filter_fields = {
            "id": ["exact"],
            "group": ["exact", "in"],
            "validity_range": ["exact", "in"],
            "validity_range__date_start": ["exact", "lt", "lte", "gt", "gte"],
            "validity_range__date_end": ["exact", "lt", "lte", "gt", "gte"],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        if not info.context.user.has_perm("lesrooster.view_timegrid_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_timegrid", queryset)
        return queryset


class TimeGridBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = TimeGrid
        permissions = ("lesrooster.create_timegrid_rule",)
        only_fields = (
            "id",
            "validity_range",
            "group",
        )


class TimeGridBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = TimeGrid
        permissions = ("lesrooster.delete_timegrid_rule",)


class TimeGridBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = TimeGrid
        permissions = ("lesrooster.edit_timegrid_rule",)
        only_fields = (
            "id",
            "validity_range",
            "group",
        )
