<script setup>
import InlineCRUDList from "aleksis.core/components/generic/InlineCRUDList.vue";
import WeekDayField from "aleksis.core/components/generic/forms/WeekDayField.vue";
import PositiveSmallIntegerField from "aleksis.core/components/generic/forms/PositiveSmallIntegerField.vue";
import TimeField from "aleksis.core/components/generic/forms/TimeField.vue";
import TimeGridField from "../validity_range/TimeGridField.vue";
</script>

<template>
  <inline-c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    :create-item-i18n-key="createItemI18nKey"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    :get-create-data="getCreateData"
    :get-patch-data="getPatchData"
    filter
  >
    <template #weekday="{ item }">
      {{ $t("weekdays." + item.weekday) }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #weekday.field="{ attrs, on }">
      <div aria-required="true">
        <week-day-field v-bind="attrs" v-on="on" :rules="required" required />
      </div>
    </template>

    <template #timeGrid="{ item }">
      {{ formatTimeGrid(item.timeGrid) }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #timeGrid.field="{ attrs, on }">
      <div aria-required="true">
        <time-grid-field v-bind="attrs" v-on="on" :rules="required" required />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #period.field="{ attrs, on }">
      <positive-small-integer-field v-bind="attrs" v-on="on" />
    </template>

    <template #timeStart="{ item }">
      {{ $d(new Date("1970-01-01T" + item.timeStart), "shortTime") }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #timeStart.field="{ attrs, on }">
      <div aria-required="true">
        <time-field v-bind="attrs" v-on="on" :rules="required" required />
      </div>
    </template>

    <template #timeEnd="{ item }">
      {{ $d(new Date("1970-01-01T" + item.timeEnd), "shortTime") }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #timeEnd.field="{ attrs, on }">
      <div aria-required="true">
        <time-field v-bind="attrs" v-on="on" :rules="required" required />
      </div>
    </template>

    <template #filters="{ attrs, on }">
      <week-day-field
        v-bind="attrs('weekday')"
        v-on="on('weekday')"
        return-int
        clearable
        :label="$t('lesrooster.slot.weekday')"
      />

      <v-row>
        <v-col>
          <positive-small-integer-field
            v-bind="attrs('period__gte')"
            v-on="on('period__gte')"
            :label="$t('lesrooster.slot.period_gte')"
          />
        </v-col>

        <v-col>
          <positive-small-integer-field
            v-bind="attrs('period__lte')"
            v-on="on('period__lte')"
            :label="$t('lesrooster.slot.period_lte')"
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col>
          <time-field
            v-bind="attrs('time_end__gte')"
            v-on="on('time_end__gte')"
            :label="$t('school_term.after')"
          />
        </v-col>
        <v-col>
          <time-field
            v-bind="attrs('time_start__lte')"
            v-on="on('time_start__lte')"
            :label="$t('school_term.before')"
          />
        </v-col>
      </v-row>
    </template>
  </inline-c-r-u-d-list>
</template>

<script>
import { slots, createSlots, deleteSlots, updateSlots } from "./slot.graphql";

export default {
  name: "LesroosterSlot",
  data() {
    return {
      headers: [
        {
          text: this.$t("lesrooster.slot.name"),
          value: "name",
        },
        {
          text: this.$t("lesrooster.validity_range.title"),
          value: "timeGrid",
          orderKey: "time_grid__validity_range__date_start",
        },
        {
          text: this.$t("lesrooster.slot.weekday"),
          value: "weekday",
        },
        {
          text: this.$t("lesrooster.slot.period"),
          value: "period",
        },
        {
          text: this.$t("lesrooster.slot.time_start"),
          value: "timeStart",
        },
        {
          text: this.$t("lesrooster.slot.time_end"),
          value: "timeEnd",
        },
      ],
      i18nKey: "lesrooster.slot",
      createItemI18nKey: "lesrooster.slot.create_slot",
      gqlQuery: slots,
      gqlCreateMutation: createSlots,
      gqlPatchMutation: updateSlots,
      gqlDeleteMutation: deleteSlots,
      defaultItem: {
        name: "",
        timeStart: "",
        timeEnd: "",
        weekday: "A_0",
        timeGrid: null,
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
  methods: {
    weekdayAsInt(weekday) {
      // Weekday is in format A_0 (monday) to A_6
      if (
        (weekday instanceof String || typeof weekday === "string") &&
        weekday.length === 3 &&
        weekday.startsWith("A_") &&
        !isNaN(parseInt(weekday.charAt(2)))
      ) {
        return parseInt(weekday.charAt(2));
      }
      console.error("Invalid Weekday:", weekday);
      return NaN;
    },
    getCreateData(item) {
      return {
        ...item,
        weekday: this.weekdayAsInt(item.weekday),
        timeGrid: item.timeGrid.id,
      };
    },
    getPatchData(item) {
      item = {
        id: item.id,
        name: item.name,
        weekday: item.weekday ? this.weekdayAsInt(item.weekday) : undefined,
        period: item.period,
        timeStart: item.timeStart,
        timeEnd: item.timeEnd,
        timeGrid: item.timeGrid?.id,
      };
      console.trace(item);
      return Object.fromEntries(
        Object.entries(item).filter(([key, value]) => value !== undefined),
      );
    },
    formatTimeGrid(item) {
      if (!item) return null;
      if (item.group === null) {
        return this.$t(
          "lesrooster.validity_range.time_grid.repr.generic",
          item.validityRange,
        );
      }
      return this.$t("lesrooster.validity_range.time_grid.repr.default", [
        item.validityRange.name,
        item.group.name,
      ]);
    },
  },
};
</script>

<style scoped></style>
