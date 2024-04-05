<script setup>
// eslint-disable-next-line no-unused-vars
import CreateSubject from "aleksis.apps.cursus/components/CreateSubject.vue";
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
import SubjectChip from "aleksis.apps.cursus/components/SubjectChip.vue";
import InlineCRUDList from "aleksis.core/components/generic/InlineCRUDList.vue";
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
    <template #breakSlot="{ item }">
      <div class="body-1">{{ formatBreakSlotItem(item.breakSlot) }}</div>
      <div class="caption">
        {{ formatTimeGridItem(item.breakSlot.timeGrid) }}
      </div>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #breakSlot.field="{ attrs, on }">
      <div aria-required="true">
        <v-autocomplete
          return-object
          :items="internalBreakSlots"
          :item-text="formatBreakSlotItem"
          item-value="id"
          :loading="$apollo.queries.internalBreakSlots.loading"
          v-bind="attrs"
          v-on="on"
        >
          <template #item="data">
            <v-list-item-content>
              <v-list-item-title>{{
                formatBreakSlotItem(data.item)
              }}</v-list-item-title>
              <v-list-item-subtitle>{{
                formatTimeGridItem(data.item.timeGrid)
              }}</v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </v-autocomplete>
      </div>
    </template>

    <template #rooms="{ item }">
      <v-chip v-for="room in item.rooms" dense class="mx-1" :key="room.id">{{
        room.shortName
      }}</v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #rooms.field="{ attrs, on }">
      <div aria-required="true">
        <v-autocomplete
          multiple
          return-object
          :items="internalRooms"
          item-text="name"
          item-value="id"
          :loading="$apollo.queries.internalRooms.loading"
          v-bind="attrs"
          v-on="on"
        />
      </div>
    </template>

    <template #teachers="{ item }">
      <v-chip
        v-for="teacher in item.teachers"
        dense
        class="mx-1"
        :key="teacher.id"
        >{{ teacher.fullName }}</v-chip
      >
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #teachers.field="{ attrs, on }">
      <div aria-required="true">
        <v-autocomplete
          multiple
          return-object
          :items="persons"
          item-text="fullName"
          item-value="id"
          v-bind="attrs"
          v-on="on"
          :loading="$apollo.queries.persons.loading"
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
      </div>
    </template>

    <template #subject="{ item }">
      <subject-chip v-if="item.subject" :subject="item.subject" />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #subject.field="{ attrs, on }">
      <foreign-key-field
        v-bind="attrs"
        v-on="on"
        :fields="subject.fields"
        :default-item="subject.defaultItem"
        :gql-query="subject.gqlQuery"
        :gql-patch-mutation="{}"
        :gql-create-mutation="subject.gqlCreateMutation"
        :get-create-data="subject.transformCreateData"
        create-item-i18n-key="cursus.subject.create"
        return-object
      >
        <template #createComponent="{ attrs: attrs2, on: on2 }">
          <create-subject v-bind="attrs2" v-on="on2"></create-subject>
        </template>
      </foreign-key-field>
    </template>

    <!--<template #filters="{ attrs, on }">-->
    <!--  <time-grid-field-->
    <!--    outlined-->
    <!--    filled-->
    <!--    v-bind="attrs('break_slot__time_grid__exact')"-->
    <!--    v-on="on('break_slot__time_grid__exact')"-->
    <!--    :label="$t('labels.select_validity_range')"-->
    <!--    hide-details-->
    <!--  />-->
    <!--</template>-->
  </inline-c-r-u-d-list>
</template>

<script>
import {
  supervisions,
  createSupervisions,
  deleteSupervisions,
  updateSupervisions,
} from "./supervision.graphql";

import { gqlTeachers } from "../helper.graphql";
import { rooms } from "aleksis.core/components/room/room.graphql";
import { breakSlots } from "../breaks_and_slots/break.graphql";
import {
  subjects,
  createSubjects,
} from "aleksis.apps.cursus/components/subject.graphql";

import { RRule } from "rrule";

export default {
  name: "LesroosterSupervision",
  data() {
    return {
      headers: [
        {
          text: this.$t("lesrooster.supervision.break_slot"),
          value: "breakSlot",
        },
        {
          text: this.$t("lesrooster.supervision.rooms"),
          value: "rooms",
        },
        {
          text: this.$t("lesrooster.supervision.teachers"),
          value: "teachers",
        },
        {
          text: this.$t("lesrooster.supervision.subject"),
          value: "subject",
        },
      ],
      i18nKey: "lesrooster.supervision",
      createItemI18nKey: "lesrooster.supervision.create_supervision",
      gqlQuery: supervisions,
      gqlCreateMutation: createSupervisions,
      gqlPatchMutation: updateSupervisions,
      gqlDeleteMutation: deleteSupervisions,
      defaultItem: {
        breakSlot: null,
        teachers: [],
        rooms: [],
      },
      subject: {
        gqlQuery: subjects,
        gqlCreateMutation: createSubjects,
        transformCreateData(item) {
          return { ...item, parent: item.parent?.id };
        },
        defaultItem: {
          name: "",
          shortName: "",
          parent: null,
          colourFg: "",
          colourBg: "",
        },
        fields: [
          {
            text: this.$t("cursus.subject.fields.name"),
            value: "name",
          },
          {
            text: this.$t("cursus.subject.fields.short_name"),
            value: "shortName",
          },
          {
            text: this.$t("cursus.subject.fields.parent"),
            value: "parent",
          },
          {
            text: this.$t("cursus.subject.fields.colour_fg"),
            value: "colourFg",
          },
          {
            text: this.$t("cursus.subject.fields.colour_bg"),
            value: "colourBg",
          },
          {
            text: this.$t("cursus.subject.fields.teachers"),
            value: "teachers",
          },
        ],
      },
      rules: {
        required: [(value) => !!value || this.$t("forms.errors.required")],
        subject: [
          (subject) => !!subject || this.$t("cursus.errors.subject_required"),
        ],
      },
    };
  },
  apollo: {
    persons: {
      query: gqlTeachers,
    },
    internalRooms: {
      query: rooms,
      update: (data) => data.items,
    },
    internalBreakSlots: {
      query: breakSlots,
      update: (data) => data.items,
    },
  },
  methods: {
    formatTimeGridItem(item) {
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
    formatBreakSlotItem(item) {
      return this.$t("lesrooster.break.repr.weekday_short", {
        weekday: this.$t("weekdays." + item.weekday),
        timeStart: item.timeStart,
        timeEnd: item.timeEnd,
      });
    },
    getRRule(timeGrid) {
      const rule = new RRule({
        freq: RRule.WEEKLY, // TODO: Make this configurable
        dtstart: new Date(timeGrid.validityRange.dateStart), // FIXME: check if this is correct with timezones etc.
        until: new Date(timeGrid.validityRange.dateEnd), // FIXME: check if this is correct with timezones etc.
      });
      return rule;
    },
    getCreateData(item) {
      return {
        breakSlot: item.breakSlot.id,
        rooms: item.rooms.map((r) => r.id),
        teachers: item.teachers.map((t) => t.id),
        subject: item.subject?.id,
        recurrence: this.getRRule(item.breakSlot.timeGrid).toString(),
      };
    },
    getPatchData(item) {
      item = {
        id: item.id,
        breakSlot: item.breakSlot?.id,
        rooms: item.rooms?.map((r) => r.id),
        teachers: item.teachers?.map((t) => t.id),
        subject: item.subject?.id,
        recurrence: this.getRRule(item.breakSlot.timeGrid).toString(),
      };
      return Object.fromEntries(
        Object.entries(item).filter(([key, value]) => value !== undefined),
      );
    },
  },
};
</script>

<style scoped></style>
