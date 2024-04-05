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
    OptimisticResponseTypeMixin,
    PermissionBatchDeleteMixin,
    PermissionBatchPatchMixin,
    PermissionsTypeMixin,
)

from ..models import Lesson


class LessonType(
    PermissionsTypeMixin, DjangoFilterMixin, OptimisticResponseTypeMixin, DjangoObjectType
):
    recurrence = graphene.String()

    class Meta:
        model = Lesson
        fields = ("id", "course", "slot_start", "slot_end", "rooms", "teachers", "subject")
        filter_fields = {
            "id": ["exact"],
            "slot_start": ["exact"],
            "slot_end": ["exact"],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        if not info.context.user.has_perm("lesrooster.view_lesson_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_lesson", queryset)
        return queryset

    @staticmethod
    def resolve_recurrence(root, info, **kwargs):
        return serialize(root.recurrence)


class LessonBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = Lesson
        only_fields = (
            "id",
            "course",
            "slot_start",
            "slot_end",
            "rooms",
            "teachers",
            "subject",
            "recurrence",
        )
        field_types = {"recurrence": graphene.String()}
        permissions = ("lesrooster.create_lesson_rule",)

    @classmethod
    def handle_recurrence(cls, value: str, name, info) -> Recurrence:
        return deserialize(value)


class LessonBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = Lesson
        permissions = ("lesrooster.delete_lesson_rule",)


class LessonBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = Lesson
        only_fields = (
            "id",
            "course",
            "slot_start",
            "slot_end",
            "rooms",
            "teachers",
            "subject",
            "recurrence",
        )
        field_types = {"recurrence": graphene.String()}
        permissions = ("lesrooster.edit_lesson_rule",)

    @classmethod
    def handle_recurrence(cls, value: str, name, info) -> Recurrence:
        return deserialize(value)
