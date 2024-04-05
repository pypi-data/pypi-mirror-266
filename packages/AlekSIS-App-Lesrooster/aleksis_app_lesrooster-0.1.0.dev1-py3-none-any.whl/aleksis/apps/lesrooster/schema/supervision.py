import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_cud.mutations import (
    DjangoBatchCreateMutation,
    DjangoBatchDeleteMutation,
    DjangoBatchPatchMutation,
)
from guardian.shortcuts import get_objects_for_user
from recurrence import Recurrence, deserialize, serialize

from aleksis.core.schema.base import (
    DjangoFilterMixin,
    PermissionBatchDeleteMixin,
    PermissionBatchPatchMixin,
    PermissionsTypeMixin,
)

from ..models import Supervision

supervision_filters = {
    "id": ["exact"],
    "rooms": ["in"],
    "teachers": ["in"],
    "subject": ["exact"],
    "break_slot": ["exact"],
    "break_slot__time_grid": ["exact"],
}


class SupervisionType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    recurrence = graphene.String()

    class Meta:
        model = Supervision
        fields = (
            "id",
            "rooms",
            "teachers",
            "subject",
            "break_slot",
        )
        filter_fields = supervision_filters

    @classmethod
    def get_queryset(cls, queryset, info):
        if not info.context.user.has_perm("lesrooster.view_supervision_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_supervision", queryset)
        return queryset

    @staticmethod
    def resolve_recurrence(root, info, **kwargs):
        return serialize(root.recurrence)


class SupervisionBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = Supervision
        field_types = {"recurrence": graphene.String()}
        only_fields = (
            "id",
            "rooms",
            "teachers",
            "subject",
            "break_slot",
            "recurrence",
        )
        permissions = ("lesrooster.create_supervision_rule",)

    @classmethod
    def handle_recurrence(cls, value: str, name, info) -> Recurrence:
        return deserialize(value)


class SupervisionBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = Supervision
        permissions = ("lesrooster.delete_supervision_rule",)


class SupervisionBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = Supervision
        only_fields = (
            "id",
            "rooms",
            "teachers",
            "subject",
            "break_slot",
            "recurrence",
        )
        field_types = {"recurrence": graphene.String()}
        exclude = ("managed_by_app_label",)
        permissions = ("lesrooster.create_supervision_rule",)

    @classmethod
    def handle_recurrence(cls, value: str, name, info) -> Recurrence:
        return deserialize(value)
