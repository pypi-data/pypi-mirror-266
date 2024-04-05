<script>
import { defineComponent } from "vue";
import ColoredShortNameChip from "../common/ColoredShortNameChip.vue";

export default defineComponent({
  name: "LessonCard",
  components: { ColoredShortNameChip },
  extends: "v-card",
  props: {
    lesson: {
      type: Object,
      required: true,
    },
    highlightedTeachers: {
      type: Array,
      required: false,
      default: () => [],
    },
    highlightedRooms: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  computed: {
    subject() {
      return (
        this.lesson.subject || {
          name: "",
          colourFg: "#000000",
          colourBg: "#e6e6e6",
        }
      );
    },
    teachers() {
      return this.lesson.teachers;
    },
    groups() {
      return this.lesson.groups;
    },
    color() {
      return this.subject.colourFg;
    },
    background() {
      return this.subject.colourBg;
    },
    loading() {
      return (
        this.lesson.isOptimistic ||
        this.lesson.id.toString().startsWith("temporary")
      );
    },
  },
  methods: {
    firstNonEmpty(...arrays) {
      return (
        arrays.find((array) => Array.isArray(array) && array.length > 0) || []
      );
    },
  },
});
</script>

<template>
  <v-card
    :color="background"
    :disabled="loading"
    class="color no-select h-100 fill-height d-flex align-center justify-center pa-0 width-title"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <div v-if="!loading" class="d-flex flex-column align-center my-1">
      <v-card-title
        class="color d-flex justify-center flex-wrap px-3 py-0 ma-0"
      >
        <span>
          <v-tooltip bottom tag="span" class="hidden-when-large">
            <template #activator="{ on, attrs }">
              <span v-bind="attrs" v-on="on" class="hidden-when-large">
                {{ subject.shortName }}
              </span>
            </template>
            <span>{{
              "course" in lesson ? lesson.course.name : lesson.name
            }}</span>
          </v-tooltip>
          <span class="hidden-when-small">{{ subject.name }}</span>
        </span>

        <v-card-subtitle
          class="caption px-3 py-0 ma-0 text-center hidden-when-small"
        >
          {{ "course" in lesson ? lesson.course.name : lesson.name }}
        </v-card-subtitle>
      </v-card-title>
      <v-card-subtitle
        class="color pa-0 ma-0 d-flex flex-wrap justify-center small-gap"
      >
        <span v-for="(teacher, index) in teachers" :key="teacher.id">
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <colored-short-name-chip
                :default-color="[color, background, true]"
                :override-color="!highlightedTeachers.includes(teacher.id)"
                v-bind="attrs"
                v-on="on"
                @click="$emit('click:teacher', teacher)"
                :item="teacher"
                :elevation="0"
              />
            </template>
            <span>{{ teacher.fullName }}</span>
          </v-tooltip>
        </span>
        <span v-for="(room, index) in lesson.rooms" :key="room.id">
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
          <span v-if="index !== 0">, </span>
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <colored-short-name-chip
                :default-color="[color, background, true]"
                :override-color="!highlightedRooms.includes(room.id)"
                v-bind="attrs"
                v-on="on"
                @click="$emit('click:room', room)"
                :item="room"
                :elevation="0"
              />
            </template>
            <span>{{ room.name }}</span>
          </v-tooltip>
        </span>
      </v-card-subtitle>
      <slot />
    </div>
    <div v-if="loading" class="text-center">
      <v-progress-circular :color="color" indeterminate />
    </div>
  </v-card>
</template>

<style scoped>
.width-title {
  container: title/inline-size;
}

.hidden-when-small {
  display: none;
}
.hidden-when-large {
  display: inline;
}

@container title (width > 150px) {
  .hidden-when-small {
    display: inline;
  }

  .hidden-when-large {
    display: none;
  }
}

.color {
  color: v-bind(color);
}

.no-select {
  user-select: none;
}

.small-gap {
  gap: 0.25rem;
}
</style>
