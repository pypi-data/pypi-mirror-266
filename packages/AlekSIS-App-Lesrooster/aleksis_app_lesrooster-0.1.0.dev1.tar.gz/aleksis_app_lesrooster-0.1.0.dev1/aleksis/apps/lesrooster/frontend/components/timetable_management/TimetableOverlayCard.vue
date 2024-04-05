<script>
import BlockingCard from "./BlockingCard.vue";
import ColoredShortNameChip from "../common/ColoredShortNameChip.vue";

export default {
  name: "TimetableOverlayCard",
  components: { ColoredShortNameChip, BlockingCard },
  props: {
    lesson: {
      type: Object,
      required: true,
    },
    weekdays: {
      type: Array,
      required: true,
    },
    periods: {
      type: Array,
      required: true,
    },
    draggedItem: {
      type: Object,
      required: true,
    },
  },
  computed: {
    x() {
      return this.weekdays.indexOf(this.lesson.slotStart.weekday) + 1;
    },
    y() {
      return this.periods.indexOf(this.lesson.slotStart.period) + 1;
    },
    w() {
      return (
        this.weekdays.indexOf(this.lesson.slotEnd.weekday) -
        this.weekdays.indexOf(this.lesson.slotStart.weekday) +
        1
      );
    },
    h() {
      return (
        this.periods.indexOf(this.lesson.slotEnd.period) -
        this.periods.indexOf(this.lesson.slotStart.period) +
        1
      );
    },
    rooms() {
      // dragged item may be a course which doesn't have a field rooms
      return this.lesson.rooms?.filter(
        (lessonRoom) =>
          !!this.draggedItem.rooms?.find((room) => room.id === lessonRoom.id),
      );
    },
    teachers() {
      return this.lesson.teachers.filter(
        (lessonTeacher) =>
          !!this.draggedItem.teachers.find(
            (teacher) => teacher.id === lessonTeacher.id,
          ),
      );
    },
  },
};
</script>

<template>
  <div>
    <blocking-card
      v-for="room in rooms"
      icon="mdi-home-off-outline"
      color="warning"
      :key="'room-' + room.id"
    >
      <colored-short-name-chip class="short" :item="room" :elevation="0" />
    </blocking-card>
    <blocking-card
      v-for="teacher in teachers"
      icon="mdi-account-off-outline"
      color="warning"
      :key="'teacher-' + teacher.id"
    >
      <colored-short-name-chip class="short" :item="teacher" :elevation="0" />
    </blocking-card>
  </div>
</template>

<style scoped>
div {
  grid-column: v-bind(x) / span v-bind(w);
  grid-row: v-bind(y) / span v-bind(h);
  z-index: 10;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 5px;
  width: 100%;
  height: 100%;
}
</style>
