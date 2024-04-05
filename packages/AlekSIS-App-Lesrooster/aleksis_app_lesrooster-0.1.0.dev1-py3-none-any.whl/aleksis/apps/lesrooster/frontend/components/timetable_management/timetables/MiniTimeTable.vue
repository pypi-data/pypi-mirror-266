<script>
import { defineComponent } from "vue";
import { slots } from "../../breaks_and_slots/slot.graphql";
import LessonCard from "../LessonCard.vue";
import MessageBox from "aleksis.core/components/generic/MessageBox.vue";

export default defineComponent({
  name: "MiniTimeTable",
  components: { LessonCard, MessageBox },
  props: {
    timeGrid: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      periods: [],
      weekdays: [],
    };
  },
  apollo: {
    slots: {
      query: slots,
      variables() {
        return {
          filters: JSON.stringify({
            time_grid: this.timeGrid.id,
          }),
        };
      },
      skip() {
        return this.timeGrid === null;
      },
      update: (data) => data.items,
      result({ data: { items } }) {
        this.weekdays = Array.from(
          new Set(
            items
              .filter((slot) => slot.model === "Slot")
              .map((slot) => slot.weekday),
          ),
        );
        this.periods = Array.from(
          new Set(
            items
              .filter((slot) => slot.model === "Slot")
              .map((slot) => slot.period),
          ),
        );
      },
    },
  },
  computed: {
    gridTemplate() {
      return (
        "[legend-row] auto " +
        this.periods.map((period) => `[period-${period}] auto `).join("") +
        "/ [legend-day] auto" +
        this.weekdays.map((weekday) => ` [${weekday}] 1fr`).join("")
      );
    },
    lessons() {
      return [];
    },
  },
  methods: {
    styleForLesson(lesson) {
      return {
        gridArea:
          `period-${lesson.slotStart.period} / ${lesson.slotStart.weekday} / ` +
          `span ${lesson.slotEnd.period - lesson.slotStart.period + 1} / ${
            lesson.slotEnd.weekday
          }`,
      };
    },
  },
});
</script>

<template>
  <div class="timetable">
    <!-- Empty div to fill top-left corner -->
    <div></div>
    <v-card
      v-for="period in periods"
      :style="{
        gridColumn: 'legend-day',
        gridRow: `period-${period} / span 1`,
      }"
      :key="'period' + period"
    >
      <v-card-text>{{ period }}</v-card-text>
    </v-card>
    <v-card
      v-for="weekday in weekdays"
      :style="{ gridRow: 'legend-row', gridColumn: `${weekday} / span 1` }"
      :key="weekday"
    >
      <v-card-text>{{ $t("weekdays." + weekday) }}</v-card-text>
    </v-card>
    <lesson-card
      v-for="lesson in lessons"
      :lesson="lesson"
      :style="styleForLesson(lesson)"
      :key="lesson.id"
    />

    <message-box type="info" v-if="!lessons || lessons.length === 0">
      {{ $t("lesrooster.timetable_management.no_lessons") }}
    </message-box>
    <message-box type="warning" v-if="!slots || slots.length === 0">
      {{ $t("lesrooster.timetable_management.no_slots") }}
    </message-box>
  </div>
</template>

<style scoped>
.timetable {
  display: grid;
  grid-template: v-bind(gridTemplate);
  gap: 1em;
}

.timetable > * {
  width: 100%;
  height: 100%;
}
</style>
