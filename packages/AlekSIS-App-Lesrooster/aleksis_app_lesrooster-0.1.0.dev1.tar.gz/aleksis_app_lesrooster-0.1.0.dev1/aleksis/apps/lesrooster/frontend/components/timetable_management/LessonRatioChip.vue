<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "LessonRatioChip",
  props: {
    course: {
      type: Object,
      required: true,
    },
  },
});
</script>

<template>
  <v-chip
    class="text-body-1 font-weight-500 px-4 mb-1"
    small
    color="white"
    light
  >
    <v-icon
      v-if="course.lessonsUsed === course.lessonQuota"
      color="green"
      left
      size="20px"
    >
      mdi-check-circle
    </v-icon>
    <v-icon
      v-else-if="course.lessonsUsed < course.lessonQuota"
      color="orange"
      left
      size="20px"
    >
      mdi-timer-sand-empty
    </v-icon>
    <v-icon v-else color="red" left size="20px"> mdi-alert </v-icon>
    {{ $t("lesrooster.timetable_management.lessons_used_ratio", course) }}
  </v-chip>
</template>

<style scoped></style>
