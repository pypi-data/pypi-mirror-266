<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "TimeGridChip",
  props: {
    value: {
      type: Object,
      required: true,
    },
    shortName: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    groupName() {
      return this.shortName ? "shortName" : "name";
    },
  },
});
</script>

<template>
  <v-chip v-bind="$attrs" v-on="$listeners" close>
    {{
      value.group?.[groupName] ||
      $t("lesrooster.validity_range.time_grid.generic")
    }}
  </v-chip>
</template>

<style scoped></style>
