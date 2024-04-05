<script>
import { defineComponent } from "vue";
import validityRangeStatuses from "./validityRangeStatuses";
export default defineComponent({
  name: "ValidityRangeStatusChip",
  props: {
    value: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      validityRangeStatuses,
    };
  },
  computed: {
    status() {
      return validityRangeStatuses[this.value];
    },
  },
});
</script>

<template>
  <v-chip v-bind="$attrs" :color="status.color" outlined>
    <v-icon left>{{ status.icon }}</v-icon>
    {{ $t(status.textKey) }}
  </v-chip>
</template>

<style scoped></style>
