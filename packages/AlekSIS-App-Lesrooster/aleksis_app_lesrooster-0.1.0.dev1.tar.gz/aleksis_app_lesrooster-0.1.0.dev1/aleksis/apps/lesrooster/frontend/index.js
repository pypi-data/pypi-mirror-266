import { hasPersonValidator } from "aleksis.core/routeValidators";

export default {
  component: () => import("aleksis.core/components/Parent.vue"),
  meta: {
    inMenu: true,
    titleKey: "lesrooster.menu_title",
    icon: "mdi-timetable",
    validators: [hasPersonValidator],
    permission: "lesrooster.view_lesrooster_menu_rule",
  },
  children: [
    {
      path: "validity_ranges/",
      component: () => import("./components/validity_range/ValidityRange.vue"),
      name: "lesrooster.validity_ranges",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.validity_range.menu_title",
        icon: "mdi-calendar-expand-horizontal-outline",
        permission: "lesrooster.view_validityranges_rule",
      },
    },
    {
      path: "raster/",
      component: () => import("./components/lesson_raster/LessonRaster.vue"),
      name: "lesrooster.lesson_raster",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.lesson_raster.menu_title",
        toolbarTitle: "lesrooster.lesson_raster.menu_title",
        icon: "mdi-grid-large",
        permission: "lesrooster.manage_lesson_raster_rule",
      },
    },
    {
      path: "timebound_course_configs/plan_courses/",
      component: () =>
        import(
          "./components/timebound_course_config/TimeboundCourseConfigRaster.vue"
        ),
      name: "lesrooster.planCourses",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.timebound_course_config.raster_menu_title",
        icon: "mdi-clock-edit-outline",
        permission: "lesrooster.view_timeboundcourseconfigs_rule",
      },
    },
    {
      path: "timetable/",
      component: () =>
        import("./components/timetable_management/TimetableManagement.vue"),
      name: "lesrooster.timetable_management_select",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.timetable_management.menu_title",
        toolbarTitle: "lesrooster.timetable_management.menu_title",
        icon: "mdi-magnet",
        permission: "lesrooster.plan_timetables_rule",
        fullWidth: true,
      },
      children: [
        {
          path: ":group(\\d+)/:timeGrid(\\d+)?/",
          component: () =>
            import("./components/timetable_management/TimetableManagement.vue"),
          name: "lesrooster.timetable_management",
          props: true,
          meta: {
            titleKey: "lesrooster.timetable_management.menu_title",
            toolbarTitle: "lesrooster.timetable_management.menu_title",
            permission: "lesrooster.plan_timetables_rule",
            fullWidth: true,
          },
        },
      ],
    },
    {
      path: "supervisions/",
      component: () => import("./components/supervision/Supervision.vue"),
      name: "lesrooster.supervisions",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.supervision.menu_title",
        icon: "mdi-seesaw",
        permission: "lesrooster.view_supervisions_rule",
      },
    },
    {
      path: "slots/",
      component: () =>
        import("./components/breaks_and_slots/LesroosterSlot.vue"),
      name: "lesrooster.slots",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.slot.menu_title",
        icon: "mdi-border-none-variant",
        permission: "lesrooster.view_slots_rule",
      },
    },
    {
      path: "breaks/",
      component: () => import("./components/breaks_and_slots/Break.vue"),
      name: "lesrooster.breaks",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.break.menu_title",
        icon: "mdi-timer-sand-paused",
        permission: "lesrooster.view_breakslots_rule",
      },
    },
    {
      path: "timebound_course_configs/",
      component: () =>
        import(
          "./components/timebound_course_config/TimeboundCourseConfigCRUDTable.vue"
        ),
      name: "lesrooster.timeboundCourseConfigs",
      meta: {
        inMenu: true,
        titleKey: "lesrooster.timebound_course_config.crud_table_menu_title",
        icon: "mdi-timetable",
        permission: "lesrooster.view_timeboundcourseconfigs_rule",
      },
    },
  ],
};
