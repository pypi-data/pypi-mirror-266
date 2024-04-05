<template>
  <v-card class="d-flex justify-space-between align-center">
    <v-card-title>{{ period }}</v-card-title>
    <div class="ma-0 py-4"><br /><br /></div>
    <v-card-subtitle
      class="ma-0 pa-4 subtitle text-right"
      v-if="timeRanges.length < 2"
    >
      {{ getTimeRangesByWeekdaysString(timeRanges?.[0]) }}
    </v-card-subtitle>
    <v-menu v-if="timeRanges.length > 1" offset-x>
      <template #activator="{ attrs, on }">
        <v-btn icon color="info" v-bind="attrs" v-on="on">
          <v-icon>$info</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item v-for="(timeRange, index) in timeRanges" :key="index">
          {{ getTimeRangesByWeekdaysString(timeRange) }}
        </v-list-item>
      </v-list>
    </v-menu>
  </v-card>
</template>

<script>
export default {
  name: "PeriodCard",
  props: {
    period: {
      type: Number,
      required: true,
    },
    weekdays: {
      type: Array,
      required: true,
    },
    timeRanges: {
      type: Array,
      required: true,
    },
  },
  methods: {
    getOutermostItems(arr) {
      const result = [];

      // Convert the input array into an array of numbers
      const numbers = arr.map((item) => parseInt(item.slice(2), 10));

      let startIndex = 0;

      for (let i = 1; i < numbers.length; i++) {
        if (numbers[i] !== numbers[i - 1] + 1) {
          result.push(arr.slice(startIndex, i));
          startIndex = i;
        }
      }

      // Push the last subarray
      result.push(arr.slice(startIndex));

      return result.map((array) =>
        array.length < 3 ? array : [array[0], array[array.length - 1]],
      );
    },
    getTimeRangesByWeekdaysString(timeRange) {
      return (
        (timeRange.weekdays.length === this.weekdays.length
          ? ""
          : this.getOutermostItems(timeRange.weekdays)
              .map(
                (weekdays) =>
                  weekdays
                    .map((weekday) => this.$t("weekdays_short." + weekday))
                    .join("‑"), // Non-breaking hyphen (U+02011)
              )
              .join(", ") + ": ") +
        this.$d(
          new Date("1970-01-01T" + timeRange.timeStart),
          "shortTime",
        ).replace(" ", " ") +
        (timeRange.weekdays.length === this.weekdays.length ? " " : "‑") + // Non-breaking hyphen (U+02011)
        this.$d(
          new Date("1970-01-01T" + timeRange.timeEnd),
          "shortTime",
        ).replace(" ", " ")
      );
    },
  },
};
</script>

<style scoped>
.subtitle {
  width: min-content;
}
</style>
