from rules import add_perm

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models import (
    BreakSlot,
    Lesson,
    Slot,
    Supervision,
    TimeboundCourseConfig,
    TimeGrid,
    ValidityRange,
)

manage_lesson_raster_predicate = has_person & has_global_perm("lesrooster.manage_lesson_raster")
add_perm("lesrooster.manage_lesson_raster_rule", manage_lesson_raster_predicate)

plan_timetables_predicate = has_person & has_global_perm("lesrooster.plan_timetables")
add_perm("lesrooster.plan_timetables_rule", plan_timetables_predicate)


# Slots
view_slots_predicate = has_person & (
    has_global_perm("lesrooster.view_slot")
    | has_any_object("lesrooster.view_slot", Slot)
    | manage_lesson_raster_predicate
    | plan_timetables_predicate
)
add_perm("lesrooster.view_slots_rule", view_slots_predicate)

view_slot_predicate = has_person & (
    has_global_perm("lesrooster.view_slot")
    | has_object_perm("lesrooster.view_slot")
    | manage_lesson_raster_predicate
    | plan_timetables_predicate
)
add_perm("lesrooster.view_slot_rule", view_slot_predicate)

create_slot_predicate = has_person & (
    has_global_perm("lesrooster.add_slot") | manage_lesson_raster_predicate
)
add_perm("lesrooster.create_slot_rule", create_slot_predicate)

edit_slot_predicate = view_slot_predicate & (
    has_global_perm("lesrooster.change_slot")
    | has_object_perm("lesrooster.change_slot")
    | manage_lesson_raster_predicate
)
add_perm("lesrooster.edit_slot_rule", edit_slot_predicate)

delete_slot_predicate = view_slot_predicate & (
    has_global_perm("lesrooster.delete_slot")
    | has_object_perm("lesrooster.delete_slot")
    | manage_lesson_raster_predicate
)
add_perm("lesrooster.delete_slot_rule", delete_slot_predicate)

# Break slots

view_break_slots_predicate = has_person & (
    has_global_perm("lesrooster.view_breakslot")
    | has_any_object("lesrooster.view_breakslot", BreakSlot)
    | manage_lesson_raster_predicate
    | plan_timetables_predicate
)
add_perm("lesrooster.view_breakslots_rule", view_break_slots_predicate)

view_break_slot_predicate = has_person & (
    has_global_perm("lesrooster.view_breakslot")
    | has_object_perm("lesrooster.view_breakslot")
    | manage_lesson_raster_predicate
    | plan_timetables_predicate
)
add_perm("lesrooster.view_breakslot_rule", view_break_slot_predicate)

create_break_slot_predicate = has_person & (
    has_global_perm("lesrooster.add_breakslot") | manage_lesson_raster_predicate
)
add_perm("lesrooster.create_breakslot_rule", create_break_slot_predicate)

edit_break_slot_predicate = view_break_slot_predicate & (
    has_global_perm("lesrooster.change_breakslot")
    | has_object_perm("lesrooster.change_breakslot")
    | manage_lesson_raster_predicate
)
add_perm("lesrooster.edit_breakslot_rule", edit_break_slot_predicate)

delete_break_slot_predicate = view_break_slot_predicate & (
    has_global_perm("lesrooster.delete_breakslot")
    | has_object_perm("lesrooster.delete_breakslot")
    | manage_lesson_raster_predicate
)
add_perm("lesrooster.delete_breakslot_rule", delete_break_slot_predicate)


# Lessons
view_lessons_predicate = has_person & (
    has_global_perm("lesrooster.view_lesson")
    | has_any_object("lesrooster.view_lesson", Lesson)
    | plan_timetables_predicate
)
add_perm("lesrooster.view_lessons_rule", view_lessons_predicate)

view_lesson_predicate = has_person & (
    has_global_perm("lesrooster.view_lesson")
    | has_object_perm("lesrooster.view_lesson")
    | plan_timetables_predicate
)
add_perm("lesrooster.view_lesson_rule", view_lesson_predicate)

create_lesson_predicate = has_person & (
    has_global_perm("lesrooster.add_lesson") | plan_timetables_predicate
)
add_perm("lesrooster.create_lesson_rule", create_lesson_predicate)

edit_lesson_predicate = view_lesson_predicate & (
    has_global_perm("lesrooster.change_lesson")
    | has_object_perm("lesrooster.change_lesson")
    | plan_timetables_predicate
)
add_perm("lesrooster.edit_lesson_rule", edit_lesson_predicate)

delete_lesson_predicate = view_lesson_predicate & (
    has_global_perm("lesrooster.delete_lesson")
    | has_object_perm("lesrooster.delete_lesson")
    | plan_timetables_predicate
)
add_perm("lesrooster.delete_lesson_rule", delete_lesson_predicate)


# Supervisions
view_supervisions_predicate = has_person & (
    has_global_perm("lesrooster.view_supervision")
    | has_any_object("lesrooster.view_supervision", Supervision)
)
add_perm("lesrooster.view_supervisions_rule", view_supervisions_predicate)

view_supervision_predicate = has_person & (
    has_global_perm("lesrooster.view_supervision") | has_object_perm("lesrooster.view_supervision")
)
add_perm("lesrooster.view_supervision_rule", view_supervision_predicate)

create_supervision_predicate = has_person & has_global_perm("lesrooster.add_supervision")
add_perm("lesrooster.create_supervision_rule", create_supervision_predicate)

edit_supervision_predicate = view_supervision_predicate & (
    has_global_perm("lesrooster.change_supervision")
    | has_object_perm("lesrooster.change_supervision")
)
add_perm("lesrooster.edit_supervision_rule", edit_supervision_predicate)

delete_supervision_predicate = view_supervision_predicate & (
    has_global_perm("lesrooster.delete_supervision")
    | has_object_perm("lesrooster.delete_supervision")
)
add_perm("lesrooster.delete_supervision_rule", delete_supervision_predicate)


# Timebound course configs

view_timebound_course_configs_predicate = has_person & (
    has_global_perm("lesrooster.view_timeboundcourseconfig")
    | has_any_object("lesrooster.view_timeboundcourseconfig", TimeboundCourseConfig)
)
add_perm("lesrooster.view_timeboundcourseconfigs_rule", view_timebound_course_configs_predicate)

view_timebound_course_config_predicate = has_person & (
    has_global_perm("lesrooster.view_timeboundcourseconfig")
    | has_object_perm("lesrooster.view_timeboundcourseconfig")
    | plan_timetables_predicate
)
add_perm("lesrooster.view_timeboundcourseconfig_rule", view_timebound_course_config_predicate)

create_timebound_course_config_predicate = has_person & has_global_perm(
    "lesrooster.add_timeboundcourseconfig"
)
add_perm("lesrooster.create_timeboundcourseconfig_rule", create_timebound_course_config_predicate)

edit_timebound_course_config_predicate = view_timebound_course_config_predicate & (
    has_global_perm("lesrooster.change_timeboundcourseconfig")
    | has_object_perm("lesrooster.change_timeboundcourseconfig")
)
add_perm("lesrooster.edit_timeboundcourseconfig_rule", edit_timebound_course_config_predicate)

delete_timebound_course_config_predicate = view_timebound_course_config_predicate & (
    has_global_perm("lesrooster.delete_timeboundcourseconfig")
    | has_object_perm("lesrooster.delete_timeboundcourseconfig")
)
add_perm("lesrooster.delete_timeboundcourseconfig_rule", delete_timebound_course_config_predicate)


# Validity ranges

view_validity_ranges_predicate = has_person & (
    has_global_perm("lesrooster.view_validityrange")
    | has_any_object("lesrooster.view_validityrange", ValidityRange)
)
add_perm("lesrooster.view_validityranges_rule", view_validity_ranges_predicate)

view_validity_range_predicate = has_person & (
    has_global_perm("lesrooster.view_validityrange")
    | has_object_perm("lesrooster.view_validityrange")
    | plan_timetables_predicate
)
add_perm("lesrooster.view_validityrange_rule", view_validity_range_predicate)

create_validity_range_predicate = has_person & has_global_perm("lesrooster.add_validityrange")
add_perm("lesrooster.create_validityrange_rule", create_validity_range_predicate)

edit_validity_range_predicate = view_validity_range_predicate & (
    has_global_perm("lesrooster.change_validityrange")
    | has_object_perm("lesrooster.change_validityrange")
)
add_perm("lesrooster.edit_validityrange_rule", edit_validity_range_predicate)

delete_validity_range_predicate = view_validity_range_predicate & (
    has_global_perm("lesrooster.delete_validityrange")
    | has_object_perm("lesrooster.delete_validityrange")
)
add_perm("lesrooster.delete_validityrange_rule", delete_validity_range_predicate)

# Time grids
view_time_grids_predicate = has_person & (
    has_global_perm("lesrooster.view_timegrid")
    | has_any_object("lesrooster.view_timegrid", TimeGrid)
)
add_perm("lesrooster.view_timegrids_rule", view_time_grids_predicate)

view_time_grid_predicate = has_person & (
    has_global_perm("lesrooster.view_timegrid")
    | has_object_perm("lesrooster.view_timegrid")
    | plan_timetables_predicate
)
add_perm("lesrooster.view_timegrid_rule", view_time_grid_predicate)

create_time_grid_predicate = has_person & has_global_perm("lesrooster.add_timegrid")
add_perm("lesrooster.create_timegrid_rule", create_time_grid_predicate)

edit_time_grid_predicate = view_time_grid_predicate & (
    has_global_perm("lesrooster.change_timegrid") | has_object_perm("lesrooster.change_timegrid")
)
add_perm("lesrooster.edit_timegrid_rule", edit_time_grid_predicate)

delete_time_grid_predicate = view_time_grid_predicate & (
    has_global_perm("lesrooster.delete_timegrid") | has_object_perm("lesrooster.delete_timegrid")
)
add_perm("lesrooster.delete_timegrid_rule", delete_time_grid_predicate)


view_lesrooster_menu_predicate = (
    view_validity_ranges_predicate
    | view_slots_predicate
    | view_break_slots_predicate
    | view_timebound_course_configs_predicate
    | manage_lesson_raster_predicate
    | plan_timetables_predicate
)
add_perm("lesrooster.view_lesrooster_menu_rule", view_lesrooster_menu_predicate)
