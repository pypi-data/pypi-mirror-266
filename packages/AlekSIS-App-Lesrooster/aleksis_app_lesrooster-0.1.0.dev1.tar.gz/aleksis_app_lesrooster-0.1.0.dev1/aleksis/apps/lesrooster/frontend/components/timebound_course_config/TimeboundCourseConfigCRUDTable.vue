<script setup>
import InlineCRUDList from "aleksis.core/components/generic/InlineCRUDList.vue";
import WeekDayField from "aleksis.core/components/generic/forms/WeekDayField.vue";
import PositiveSmallIntegerField from "aleksis.core/components/generic/forms/PositiveSmallIntegerField.vue";
import TimeField from "aleksis.core/components/generic/forms/TimeField.vue";
import ValidityRangeField from "../validity_range/ValidityRangeField.vue";
import SubjectChip from "aleksis.apps.cursus/components/SubjectChip.vue";
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
    <template #course="{ item }">
      {{ item.course.name }}
      <subject-chip v-if="item.course.subject" :subject="item.course.subject" />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #course.field="{ attrs, on }">
      <v-autocomplete
        :items="courses"
        item-text="name"
        item-value="id"
        v-bind="attrs"
        v-on="on"
        return-object
      />
    </template>

    <template #validityRange="{ item }">
      {{ item.validityRange?.name }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #validityRange.field="{ attrs, on }">
      <validity-range-field v-bind="attrs" v-on="on" :rules="required" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #lessonQuota.field="{ attrs, on }">
      <positive-small-integer-field
        v-bind="attrs"
        v-on="on"
        :rules="required"
      />
    </template>

    <template #teachers="{ item }">
      <v-chip v-for="teacher in item.teachers" :key="teacher.id">{{
        teacher.fullName
      }}</v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #teachers.field="{ attrs, on }">
      <v-autocomplete
        multiple
        :items="persons"
        item-text="fullName"
        item-value="id"
        v-bind="attrs"
        v-on="on"
        chips
        deletable-chips
        return-object
      >
        <template #item="data">
          <v-list-item-action>
            <v-checkbox v-model="data.attrs.inputValue" />
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>{{ data.item.fullName }}</v-list-item-title>
            <v-list-item-subtitle v-if="data.item.shortName">{{
              data.item.shortName
            }}</v-list-item-subtitle>
          </v-list-item-content>
        </template>
      </v-autocomplete>
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
import {
  timeboundCourseConfigs,
  createTimeboundCourseConfigs,
  deleteTimeboundCourseConfigs,
  updateTimeboundCourseConfigs,
} from "./timeboundCourseConfig.graphql";

import { currentValidityRange as gqlCurrentValidityRange } from "../validity_range/validityRange.graphql";

import { gqlPersons, gqlCourses } from "../helper.graphql";

export default {
  name: "TimeboungCourseConfigCRUDTable",
  data() {
    return {
      headers: [
        {
          text: this.$t("lesrooster.timebound_course_config.course"),
          value: "course",
        },
        {
          text: this.$t("lesrooster.validity_range.title"),
          value: "validityRange",
          orderKey: "validity_range__date_start",
        },
        {
          text: this.$t("lesrooster.timebound_course_config.teachers"),
          value: "teachers",
        },
        {
          text: this.$t("lesrooster.timebound_course_config.lesson_quota"),
          value: "lessonQuota",
        },
      ],
      i18nKey: "lesrooster.timebound_course_config",
      createItemI18nKey:
        "lesrooster.timebound_course_config.create_timebound_course_config",
      gqlQuery: timeboundCourseConfigs,
      gqlCreateMutation: createTimeboundCourseConfigs,
      gqlPatchMutation: updateTimeboundCourseConfigs,
      gqlDeleteMutation: deleteTimeboundCourseConfigs,
      defaultItem: {
        course: {
          id: "",
          name: "",
        },
        validityRange: {
          id: "",
          name: "",
        },
        teachers: [],
        lessonQuota: undefined,
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
  methods: {
    getCreateData(item) {
      return {
        ...item,
        course: item.course.id,
        teachers: item.teachers.map((t) => t.id),
        validityRange: item.validityRange.id,
      };
    },
    getPatchData(item) {
      item = {
        id: item.id,
        course: item.course?.id,
        teachers: item.teachers?.map((t) => t.id),
        validityRange: item.validityRange?.id,
        lessonQuota: item.lessonQuota,
      };
      return Object.fromEntries(
        Object.entries(item).filter(([key, value]) => value !== undefined),
      );
    },
  },
  apollo: {
    currentValidityRange: {
      query: gqlCurrentValidityRange,
      result({ data }) {
        this.$set(this.defaultItem, "validityRange", data.currentValidityRange);
      },
    },
    persons: gqlPersons,
    courses: gqlCourses,
  },
};
</script>

<style scoped></style>
