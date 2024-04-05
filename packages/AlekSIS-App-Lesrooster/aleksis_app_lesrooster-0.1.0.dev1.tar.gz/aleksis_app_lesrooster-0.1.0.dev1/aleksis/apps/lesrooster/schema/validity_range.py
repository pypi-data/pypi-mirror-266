import graphene
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

from ..models import ValidityRange


class ValidityRangeType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    is_current = graphene.Boolean()

    class Meta:
        model = ValidityRange
        fields = ("id", "school_term", "name", "date_start", "date_end", "status", "time_grids")
        filter_fields = {
            "id": ["exact"],
            "school_term": ["exact", "in"],
            "status": ["exact"],
            "name": ["icontains", "exact"],
            "date_start": ["exact", "lt", "lte", "gt", "gte"],
            "date_end": ["exact", "lt", "lte", "gt", "gte"],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        if not info.context.user.has_perm("lesrooster.view_validityrange_rule"):
            return get_objects_for_user(
                info.context.user, "lesrooster.view_validityrange", queryset
            )
        return queryset


class ValidityRangeBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = ValidityRange
        permissions = ("lesrooster.create_validity_range_rule",)
        only_fields = (
            "id",
            "school_term",
            "name",
            "date_start",
            "date_end",
            "status",
            "time_grids",
        )
        field_types = {"status": graphene.String()}


class ValidityRangeBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = ValidityRange
        permissions = ("lesrooster.delete_validityrange_rule",)


class ValidityRangeBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = ValidityRange
        permissions = ("lesrooster.change_validityrange",)
        only_fields = (
            "id",
            "school_term",
            "name",
            "date_start",
            "date_end",
            "status",
            "time_grids",
        )
        field_types = {"status": graphene.String()}
