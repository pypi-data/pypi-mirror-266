from django.core.exceptions import PermissionDenied

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

from ..models import BreakSlot, Slot, TimeGrid

slot_filters = {
    "id": ["exact"],
    "name": ["exact", "icontains"],
    "weekday": ["exact", "in"],
    "period": ["exact", "lt", "lte", "gt", "gte"],
    "time_start": ["exact", "lt", "lte", "gt", "gte"],
    "time_end": ["exact", "lt", "lte", "gt", "gte"],
    "time_grid": ["exact"],
}


class SlotType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    model = graphene.String(default_value="Default")

    class Meta:
        model = Slot
        fields = ("id", "time_grid", "name", "weekday", "period", "time_start", "time_end")
        filter_fields = slot_filters

    @classmethod
    def get_queryset(cls, queryset, info):
        if not info.context.user.has_perm("lesrooster.view_slot_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_slot", queryset)
        return queryset

    @staticmethod
    def resolve_model(root, info):
        return root.get_real_instance_class().__name__


class SlotBatchCreateMutation(PermissionBatchPatchMixin, DjangoBatchCreateMutation):
    class Meta:
        model = Slot
        field_types = {"weekday": graphene.Int()}
        only_fields = ("id", "time_grid", "name", "weekday", "period", "time_start", "time_end")
        permissions = ("lesrooster.create_slot_rule",)


class SlotBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = Slot
        permissions = ("lesrooster.delete_slot",)


class SlotBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = Slot
        field_types = {"weekday": graphene.Int()}
        permissions = ("lesrooster.change_slot",)
        only_fields = ("id", "time_grid", "name", "weekday", "period", "time_start", "time_end")


class CarryOverSlotsMutation(graphene.Mutation):
    class Arguments:
        time_grid = graphene.ID()
        from_day = graphene.Int()
        to_day = graphene.Int()

        only = graphene.List(graphene.ID, required=False)

    deleted = graphene.List(graphene.ID)
    result = graphene.List(SlotType)

    @classmethod
    def mutate(cls, root, info, time_grid, from_day, to_day, only=None):
        if not info.context.user.has_perm("lesrooster.edit_slot_rule"):
            raise PermissionDenied()

        if only is None:
            only = []

        time_grid = TimeGrid.objects.get(id=time_grid)

        slots_on_day = Slot.objects.filter(weekday=from_day, time_grid=time_grid)

        if only and len(only) > 0:
            slots_on_day = slots_on_day.filter(id__in=only)

        result = []
        new_ids = []

        for slot in slots_on_day:
            defaults = {"name": slot.name, "time_start": slot.time_start, "time_end": slot.time_end}

            if slot.period is not None:
                new_slot = Slot.objects.non_polymorphic().update_or_create(
                    weekday=to_day, time_grid=time_grid, period=slot.period, defaults=defaults
                )[0]

            else:
                new_slot = Slot.objects.non_polymorphic().update_or_create(
                    weekday=to_day,
                    time_grid=time_grid,
                    time_start=slot.time_start,
                    time_end=slot.time_end,
                    defaults=defaults,
                )[0]

            result.append(new_slot)
            new_ids.append(new_slot.pk)

        if not only or not len(only):
            objects_to_delete = Slot.objects.filter(weekday=to_day, time_grid=time_grid).exclude(
                pk__in=new_ids
            )
            objects_to_delete.delete()

            deleted = objects_to_delete.values_list("id", flat=True)

        else:
            deleted = []

        return CarryOverSlotsMutation(
            deleted=deleted,
            result=result,
        )


class CopySlotsFromDifferentTimeGridMutation(graphene.Mutation):
    class Arguments:
        time_grid = graphene.ID()
        from_time_grid = graphene.ID()

    deleted = graphene.List(graphene.ID)
    result = graphene.List(SlotType)

    @classmethod
    def mutate(cls, root, info, time_grid, from_time_grid):
        if not info.context.user.has_perm("lesrooster.edit_slot_rule"):
            raise PermissionDenied()

        time_grid = TimeGrid.objects.get(id=time_grid)
        from_time_grid = TimeGrid.objects.get(id=from_time_grid)

        # Check for each slot in the from_time_grid if it exists in the time_grid, if not, create it
        slots = Slot.objects.filter(time_grid=from_time_grid)

        result = []

        for slot in slots:
            slot: BreakSlot | Slot
            klass = slot.get_real_instance_class()

            defaults = {"name": slot.name, "time_start": slot.time_start, "time_end": slot.time_end}

            result.append(
                klass.objects.update_or_create(
                    weekday=slot.weekday, time_grid=time_grid, period=slot.period, defaults=defaults
                )[0].id
            )

        # Delete all slots in the time_grid that are not in the from_time_grid
        objects_to_delete = Slot.objects.filter(time_grid=time_grid).exclude(id__in=result)
        objects_to_delete.delete()

        deleted = objects_to_delete.values_list("id", flat=True)

        return CopySlotsFromDifferentTimeGridMutation(
            deleted=deleted,
            result=Slot.objects.filter(time_grid=time_grid).non_polymorphic(),
        )
