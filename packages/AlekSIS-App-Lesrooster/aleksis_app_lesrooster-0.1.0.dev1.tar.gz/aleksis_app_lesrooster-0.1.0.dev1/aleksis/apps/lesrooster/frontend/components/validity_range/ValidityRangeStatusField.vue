<template>
  <v-select v-bind="$attrs" v-on="$listeners" :items="items" item-value="value">
    <template #selection="{ item, index }">
      <validity-range-status-chip :value="item.value" />
    </template>
  </v-select>
</template>

<script>
import validityRangeStatuses from "./validityRangeStatuses";
import ValidityRangeStatusChip from "./ValidityRangeStatusChip.vue";
export default {
  name: "ValidityRangeStatusField",
  extends: "v-select",
  components: { ValidityRangeStatusChip },
  data() {
    return {
      items: Object.values(validityRangeStatuses).map((item) => {
        return { ...item, text: this.$t(item.textKey) };
      }),
    };
  },
};
</script>
