from itertools import chain

from django.db.models import Prefetch, Q

import graphene
from guardian.shortcuts import get_objects_for_user

from aleksis.apps.cursus.models import Course, Subject
from aleksis.apps.cursus.schema import CourseInterface
from aleksis.core.models import Group
from aleksis.core.schema.base import FilterOrderList
from aleksis.core.schema.group import GroupType

from ..models import (
    BreakSlot,
    Lesson,
    Slot,
    Supervision,
    TimeboundCourseConfig,
    TimeGrid,
    ValidityRange,
)
from .break_slot import (
    BreakSlotBatchCreateMutation,
    BreakSlotBatchDeleteMutation,
    BreakSlotBatchPatchMutation,
    BreakSlotType,
)
from .lesson import (
    LessonBatchCreateMutation,
    LessonBatchDeleteMutation,
    LessonBatchPatchMutation,
    LessonType,
)
from .slot import (
    CarryOverSlotsMutation,
    CopySlotsFromDifferentTimeGridMutation,
    SlotBatchCreateMutation,
    SlotBatchDeleteMutation,
    SlotBatchPatchMutation,
    SlotType,
)
from .supervision import (
    SupervisionBatchCreateMutation,
    SupervisionBatchDeleteMutation,
    SupervisionBatchPatchMutation,
    SupervisionType,
)
from .time_grid import (
    TimeGridBatchCreateMutation,
    TimeGridBatchDeleteMutation,
    TimeGridType,
)
from .timebound_course_config import (
    LesroosterExtendedSubjectType,
    TimeboundCourseConfigBatchCreateMutation,
    TimeboundCourseConfigBatchDeleteMutation,
    TimeboundCourseConfigBatchPatchMutation,
    TimeboundCourseConfigType,
)
from .validity_range import (
    ValidityRangeBatchCreateMutation,
    ValidityRangeBatchDeleteMutation,
    ValidityRangeBatchPatchMutation,
    ValidityRangeType,
)


class Query(graphene.ObjectType):
    break_slots = FilterOrderList(BreakSlotType)
    slots = FilterOrderList(SlotType)
    timebound_course_configs = FilterOrderList(TimeboundCourseConfigType)
    validity_ranges = FilterOrderList(ValidityRangeType)
    time_grids = FilterOrderList(TimeGridType)
    lessons = FilterOrderList(LessonType)
    supervisions = FilterOrderList(SupervisionType)

    course_objects_for_group = graphene.List(
        CourseInterface,
        group=graphene.ID(required=True),
        time_grid=graphene.ID(required=True),
    )
    lesson_objects_for_group = graphene.List(
        LessonType,
        group=graphene.ID(required=True),
        time_grid=graphene.ID(required=True),
    )
    lesson_objects_for_teacher = graphene.List(
        LessonType,
        teacher=graphene.ID(required=True),
        time_grid=graphene.ID(required=True),
    )
    lesson_objects_for_room = graphene.List(
        LessonType,
        room=graphene.ID(required=True),
        time_grid=graphene.ID(required=True),
    )

    lessons_objects_for_rooms_or_teachers = graphene.List(
        LessonType,
        rooms=graphene.List(graphene.ID, required=True),
        teachers=graphene.List(graphene.ID, required=True),
        time_grid=graphene.ID(required=True),
    )

    current_validity_range = graphene.Field(ValidityRangeType)

    lesrooster_extended_subjects = FilterOrderList(
        LesroosterExtendedSubjectType, groups=graphene.List(graphene.ID)
    )

    groups_by_time_grid = graphene.List(GroupType, time_grid=graphene.ID(required=True))

    @staticmethod
    def resolve_break_slots(root, info):
        if not info.context.user.has_perm("lesrooster.view_breakslot_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_breakslot", BreakSlot)
        return BreakSlot.objects.all()

    @staticmethod
    def resolve_slots(root, info):
        # Note: This does also return `Break` objects (but with type set to Slot). This is intended
        slots = Slot.objects.non_polymorphic()
        if not info.context.user.has_perm("lesrooster.view_slot_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_slot", slots)
        return slots

    @staticmethod
    def resolve_timebound_course_configs(root, info):
        tccs = TimeboundCourseConfig.objects.all()
        if not info.context.user.has_perm("lesrooster.view_timeboundcourseconfig_rule"):
            return get_objects_for_user(
                info.context.user, "lesrooster.view_timeboundcourseconfig", tccs
            )
        return tccs

    @staticmethod
    def resolve_validity_ranges(root, info):
        if not info.context.user.has_perm("lesrooster.view_validityrange_rule"):
            return get_objects_for_user(
                info.context.user, "lesrooster.view_validityrange", ValidityRange
            )
        return ValidityRange.objects.all()

    @staticmethod
    def resolve_time_grids(root, info):
        if not info.context.user.has_perm("lesrooster.view_timegrid_rule"):
            return get_objects_for_user(info.context.user, "lesrooster.view_timegrid", TimeGrid)
        return TimeGrid.objects.all()

    @staticmethod
    def resolve_supervisions(root, info):
        if not info.context.user.has_perm("lesrooster.view_supervision_rule"):
            return get_objects_for_user(
                info.context.user, "lesrooster.view_supervision", Supervision
            )
        return Supervision.objects.all()

    @staticmethod
    def resolve_lesrooster_extended_subjects(root, info, groups):
        subjects = Subject.objects.all().prefetch_related(
            Prefetch(
                "courses",
                queryset=get_objects_for_user(
                    info.context.user, "cursus.view_course", Course.objects.all()
                ).filter(groups__in=groups),
            )
        )
        if not info.context.user.has_perm("lesrooster.view_subject_rule"):
            return get_objects_for_user(info.context.user, "cursus.view_subject", subjects)
        return subjects

    @staticmethod
    def resolve_current_validity_range(root, info):
        validity_range = ValidityRange.current
        if info.context.user.has_perm("lesrooster.view_validityrange_rule", validity_range):
            return validity_range

    def resolve_course_objects_for_group(root, info, group, time_grid):
        if not info.context.user.has_perm("lesrooster.plan_timetables_rule"):
            return []

        group = Group.objects.get(pk=group)

        if not group:
            return []

        courses = Course.objects.filter(
            (Q(groups__in=group.child_groups.all()) | Q(groups=group))
            & Q(lr_timebound_course_configs__isnull=True)
        )

        timebound_course_configs = TimeboundCourseConfig.objects.filter(
            Q(validity_range__time_grids__in=time_grid)
            & (Q(course__groups__in=group.child_groups.all()) | Q(course__groups=group))
        )

        return list(chain(courses, timebound_course_configs))

    @staticmethod
    def resolve_lesson_objects_for_group(root, info, group, time_grid):
        if not info.context.user.has_perm("lesrooster.plan_timetables_rule"):
            return []

        group = Group.objects.get(pk=group)

        if not group:
            return []

        courses = Course.objects.filter(Q(groups__in=group.child_groups.all()) | Q(groups=group))

        return Lesson.objects.filter(
            course__in=courses,
            slot_start__time_grid_id=time_grid,
            slot_end__time_grid_id=time_grid,
        )

    @staticmethod
    def resolve_lesson_objects_for_teacher(root, info, teacher, time_grid):
        if not info.context.user.has_perm("lesrooster.plan_timetables_rule"):
            return []

        return Lesson.objects.filter(
            Q(teachers=teacher) | Q(course__teachers=teacher),
            slot_start__time_grid_id=time_grid,
            slot_end__time_grid_id=time_grid,
        ).distinct()

    @staticmethod
    def resolve_lesson_objects_for_room(root, info, room, time_grid):
        if not info.context.user.has_perm("lesrooster.plan_timetables_rule"):
            return []

        return Lesson.objects.filter(
            rooms=room,
            slot_start__time_grid_id=time_grid,
            slot_end__time_grid_id=time_grid,
        ).distinct()

    @staticmethod
    def resolve_lessons_objects_for_rooms_or_teachers(
        root, info, time_grid, rooms=None, teachers=None
    ):
        if teachers is None:
            teachers = []
        if rooms is None:
            rooms = []
        if not info.context.user.has_perm("lesrooster.plan_timetables_rule"):
            return []

        return Lesson.objects.filter(
            Q(rooms__in=rooms) | Q(teachers__in=teachers) | Q(course__teachers__in=teachers),
            slot_start__time_grid_id=time_grid,
            slot_end__time_grid_id=time_grid,
        ).distinct()

    @staticmethod
    def resolve_groups_by_time_grid(root, info, time_grid=None, **kwargs):
        if not info.context.user.has_perm("lesrooster.plan_timetables_rule"):
            return []

        # This will fail if the ID is invalid, but won't, if it is empty
        time_grid_obj: TimeGrid | None = (
            TimeGrid.objects.get(pk=time_grid) if time_grid is not None else None
        )

        # If there is no time_grid, or it is a generic one, filter groups
        # to have a fitting school_term
        if time_grid_obj is None or time_grid_obj.group is None:
            return (
                Group.objects.filter(school_term__lr_validity_ranges__time_grids__id=time_grid)
                .annotate(has_cg=Q(child_groups__isnull=False))
                .order_by("-has_cg", "name")
            )

        group_id = time_grid_obj.group.pk

        return (
            Group.objects.filter(
                Q(pk=group_id)
                | Q(parent_groups=group_id)
                | Q(parent_groups__parent_groups=group_id)
            )
            .distinct()
            .annotate(has_cg=Q(child_groups__isnull=False))
            .order_by("-has_cg", "name")
        )


class Mutation(graphene.ObjectType):
    create_break_slots = BreakSlotBatchCreateMutation.Field()
    delete_break_slots = BreakSlotBatchDeleteMutation.Field()
    update_break_slots = BreakSlotBatchPatchMutation.Field()

    create_slots = SlotBatchCreateMutation.Field()
    delete_slots = SlotBatchDeleteMutation.Field()
    update_slots = SlotBatchPatchMutation.Field()

    create_timebound_course_configs = TimeboundCourseConfigBatchCreateMutation.Field()
    delete_timebound_course_configs = TimeboundCourseConfigBatchDeleteMutation.Field()
    update_timebound_course_configs = TimeboundCourseConfigBatchPatchMutation.Field()
    carry_over_slots = CarryOverSlotsMutation.Field()
    copy_slots_from_grid = CopySlotsFromDifferentTimeGridMutation.Field()

    create_validity_ranges = ValidityRangeBatchCreateMutation.Field()
    delete_validity_ranges = ValidityRangeBatchDeleteMutation.Field()
    update_validity_ranges = ValidityRangeBatchPatchMutation.Field()

    create_time_grids = TimeGridBatchCreateMutation.Field()
    delete_time_grids = TimeGridBatchDeleteMutation.Field()
    update_time_grids = TimeGridBatchDeleteMutation.Field()

    create_lessons = LessonBatchCreateMutation.Field()
    delete_lessons = LessonBatchDeleteMutation.Field()
    update_lessons = LessonBatchPatchMutation.Field()

    create_supervisions = SupervisionBatchCreateMutation.Field()
    delete_supervisions = SupervisionBatchDeleteMutation.Field()
    update_supervisions = SupervisionBatchPatchMutation.Field()
