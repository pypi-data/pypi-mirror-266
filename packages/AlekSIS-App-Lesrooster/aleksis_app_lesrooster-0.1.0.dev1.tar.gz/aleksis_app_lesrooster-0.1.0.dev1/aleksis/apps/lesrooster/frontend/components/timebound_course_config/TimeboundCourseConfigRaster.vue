<script setup>
import PositiveSmallIntegerField from "aleksis.core/components/generic/forms/PositiveSmallIntegerField.vue";
import SaveButton from "aleksis.core/components/generic/buttons/SaveButton.vue";
import SecondaryActionButton from "aleksis.core/components/generic/buttons/SecondaryActionButton.vue";
import ValidityRangeField from "../validity_range/ValidityRangeField.vue";
import SubjectChip from "aleksis.apps.cursus/components/SubjectChip.vue";
</script>

<template>
  <div>
    <v-data-table
      disable-sort
      disable-filtering
      disable-pagination
      hide-default-footer
      :headers="headers"
      :items="tableItems"
    >
      <template #top>
        <v-row>
          <v-col
            cols="6"
            lg="3"
            class="d-flex justify-space-between flex-wrap align-center"
          >
            <v-autocomplete
              outlined
              filled
              multiple
              hide-details
              :items="groups"
              item-text="shortName"
              item-value="id"
              return-object
              :disabled="$apollo.queries.groups.loading"
              :label="$t('lesrooster.timebound_course_config.groups')"
              :loading="$apollo.queries.groups.loading"
              v-model="selectedGroups"
              class="mr-4"
            />
          </v-col>

          <v-col
            cols="6"
            lg="3"
            class="d-flex justify-space-between flex-wrap align-center"
          >
            <validity-range-field
              outlined
              filled
              label="Select Validity Range"
              hide-details
              v-model="internalValidityRange"
              :loading="$apollo.queries.currentValidityRange.loading"
            />
          </v-col>

          <v-spacer />

          <v-col
            cols="8"
            lg="3"
            class="d-flex justify-space-between flex-wrap align-center"
          >
            <secondary-action-button
              i18n-key="actions.copy_last_configuration"
              block
              class="mr-4"
            />
          </v-col>
          <v-col
            cols="4"
            lg="1"
            class="d-flex justify-space-between flex-wrap align-center"
          >
            <save-button
              :disabled="
                !editedCourseConfigs.length &&
                !createdCourseConfigs.length &&
                !createdCourses.length
              "
              @click="save"
            />
          </v-col>
        </v-row>
      </template>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #item.subject="{ item, value }">
        <subject-chip v-if="value" :subject="value" />
      </template>

      <template
        v-for="(groupHeader, index) in groupHeaders"
        #[tableItemSlotName(groupHeader)]="{ item, value, header }"
      >
        <div :key="index">
          <div v-if="value.length">
            <v-row
              v-for="(course, index) in value"
              :key="index"
              no-gutters
              class="mt-2"
            >
              <v-col cols="6">
                <positive-small-integer-field
                  dense
                  filled
                  class="mx-1"
                  :disabled="loading"
                  :value="
                    getCurrentCourseConfig(course)
                      ? getCurrentCourseConfig(course).lessonQuota
                      : course.lessonQuota
                  "
                  :label="$t('lesrooster.timebound_course_config.lesson_quota')"
                  @input="
                    (event) =>
                      setCourseConfigData(course, item.subject, header, {
                        lessonQuota: event,
                      })
                  "
                />
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  counter
                  dense
                  filled
                  multiple
                  :items="getTeacherList(item.subject.teachers)"
                  item-text="fullName"
                  item-value="id"
                  class="mx-1"
                  :disabled="loading"
                  :label="$t('lesrooster.timebound_course_config.teachers')"
                  :value="
                    getCurrentCourseConfig(course)
                      ? getCurrentCourseConfig(course).teachers
                      : course.teachers
                  "
                  @input="
                    (event) =>
                      setCourseConfigData(course, item.subject, header, {
                        teachers: event,
                      })
                  "
                >
                  <template #item="data">
                    <template v-if="typeof data.item !== 'object'">
                      <v-list-item-content>{{ data.item }}</v-list-item-content>
                    </template>
                    <template v-else>
                      <v-list-item-action>
                        <v-checkbox v-model="data.attrs.inputValue" />
                      </v-list-item-action>
                      <v-list-item-content>
                        <v-list-item-title>{{
                          data.item.fullName
                        }}</v-list-item-title>
                        <v-list-item-subtitle v-if="data.item.shortName">{{
                          data.item.shortName
                        }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </template>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>
          </div>
          <div v-if="!value.length">
            <v-btn
              block
              icon
              tile
              outlined
              @click="addCourse(item.subject.id, header.value)"
            >
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>
        </div>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import {
  subjects,
  createTimeboundCourseConfigs,
  updateTimeboundCourseConfigs,
} from "./timeboundCourseConfig.graphql";

import { currentValidityRange as gqlCurrentValidityRange } from "../validity_range/validityRange.graphql";

import { gqlGroups, gqlTeachers } from "../helper.graphql";

import { createCourses } from "aleksis.apps.cursus/components/course.graphql";

export default {
  name: "TimeboungCourseConfigRaster",
  data() {
    return {
      i18nKey: "lesrooster.timebound_course_config",
      createItemI18nKey:
        "lesrooster.timebound_course_config.create_timebound_course_config",
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
      internalValidityRange: null,
      groups: [],
      selectedGroups: [],
      subjects: [],
      editedCourseConfigs: [],
      createdCourseConfigs: [],
      newCourses: [],
      createdCourses: [],
      currentCourse: null,
      currentSubject: null,
      loading: false,
    };
  },
  methods: {
    tableItemSlotName(header) {
      return "item." + header.value;
    },
    getCurrentCourseConfig(course) {
      if (course.lrTimeboundCourseConfigs?.length) {
        let currentCourseConfigs = course.lrTimeboundCourseConfigs.filter(
          (timeboundConfig) =>
            timeboundConfig.validityRange.id === this.internalValidityRange.id,
        );
        if (currentCourseConfigs.length) {
          return currentCourseConfigs[0];
        } else {
          return null;
        }
      } else {
        return null;
      }
    },
    setCourseConfigData(course, subject, header, newValue) {
      if (course.newCourse) {
        let existingCreatedCourse = this.createdCourses.find(
          (c) =>
            c.subject === subject.id &&
            JSON.stringify(c.groups) === header.value,
        );
        if (!existingCreatedCourse) {
          this.createdCourses.push({
            subject: subject.id,
            groups: JSON.parse(header.value),
            name: `${header.text}-${subject.name}`,
            ...newValue,
          });
        } else {
          Object.assign(existingCreatedCourse, newValue);
        }
      } else {
        if (
          !course.lrTimeboundCourseConfigs?.filter(
            (c) => c.validityRange.id === this.internalValidityRange?.id,
          ).length
        ) {
          let existingCreatedCourseConfig = this.createdCourseConfigs.find(
            (c) =>
              c.course === course.id &&
              c.validityRange === this.internalValidityRange?.id,
          );
          if (!existingCreatedCourseConfig) {
            this.createdCourseConfigs.push({
              course: course.id,
              validityRange: this.internalValidityRange?.id,
              teachers: course.teachers.map((t) => t.id),
              lessonQuota: course.lessonQuota,
              ...newValue,
            });
          } else {
            Object.assign(existingCreatedCourseConfig, newValue);
          }
        } else {
          let courseConfigID = course.lrTimeboundCourseConfigs[0].id;
          let existingEditedCourseConfig = this.editedCourseConfigs.find(
            (c) => c.id === courseConfigID,
          );
          if (!existingEditedCourseConfig) {
            this.editedCourseConfigs.push({ id: courseConfigID, ...newValue });
          } else {
            Object.assign(existingEditedCourseConfig, newValue);
          }
        }
      }
    },
    save() {
      this.loading = true;

      for (let mutationCombination of [
        {
          data: this.editedCourseConfigs,
          mutation: updateTimeboundCourseConfigs,
        },
        {
          data: this.createdCourseConfigs,
          mutation: createTimeboundCourseConfigs,
        },
        {
          data: this.createdCourses,
          mutation: createCourses,
        },
      ]) {
        if (mutationCombination.data.length) {
          this.$apollo
            .mutate({
              mutation: mutationCombination.mutation,
              variables: {
                input: mutationCombination.data,
              },
            })
            .catch(() => {}); // FIXME Error Handling
        }
      }

      this.editedCourseConfigs = [];
      this.createdCourseConfigs = [];
      this.createdCourses = [];
      this.$apollo.queries.subjects.refetch();
      this.loading = false;
    },
    getTeacherList(subjectTeachers) {
      return [
        {
          header: this.$t(
            "lesrooster.timebound_course_config.subject_teachers",
          ),
        },
        ...this.persons.filter((person) =>
          subjectTeachers.find((teacher) => teacher.id === person.id),
        ),
        { divider: true },
        { header: this.$t("lesrooster.timebound_course_config.all_teachers") },
        ...this.persons.filter(
          (person) =>
            !subjectTeachers.find((teacher) => teacher.id === person.id),
        ),
      ];
    },
    addCourse(subject, groups) {
      let courseSubjectGroup = this.newCourses.find(
        (courseSubject) => courseSubject.subject === subject,
      );
      if (courseSubjectGroup) {
        if (courseSubjectGroup.groupCombinations) {
          this.$set(courseSubjectGroup.groupCombinations, groups, [
            { teachers: [], newCourse: true },
          ]);
        } else {
          courseSubjectGroup.groupCombinations = {
            [groups]: [{ teachers: [], newCourse: true }],
          };
        }
      } else {
        this.newCourses.push({
          subject: subject,
          groupCombinations: { [groups]: [{ teachers: [], newCourse: true }] },
        });
      }
    },
  },
  computed: {
    groupIDList() {
      return this.selectedGroups.map((group) => group.id);
    },
    subjectGroupCombinations() {
      return [].concat.apply(
        [],
        this.items.map((subject) => Object.keys(subject.groupCombinations)),
      );
    },
    groupHeaders() {
      return this.selectedGroups
        .map((group) => ({
          text: group.shortName,
          value: JSON.stringify([group.id]),
        }))
        .concat(
          this.subjectGroupCombinations.map((combination) => {
            let parsedCombination = JSON.parse(combination);
            return {
              text: parsedCombination
                .map(
                  (groupID) =>
                    this.groups.find((group) => group.id === groupID).shortName,
                )
                .join(", "),
              value: combination,
            };
          }),
        )
        .filter(
          (obj, index, self) =>
            index === self.findIndex((o) => o.value === obj.value),
        );
    },
    headers() {
      let groupHeadersWithWidth = this.groupHeaders.map((header) => ({
        ...header,
        width: `${Math.max(95 / this.groupHeaders.length, 15)}vw`,
      }));
      return [
        {
          text: this.$t("lesrooster.timebound_course_config.subject"),
          value: "subject",
          width: "5%",
        },
      ].concat(groupHeadersWithWidth);
    },
    items() {
      return this.subjects.map((subject) => {
        let groupCombinations = {};

        subject.courses.forEach((course) => {
          let groupIds = JSON.stringify(
            course.groups.map((group) => group.id).sort(),
          );

          if (!groupCombinations[groupIds]) {
            groupCombinations[groupIds] = [];
          }

          if (!groupCombinations[groupIds].find((c) => c.id === course.id)) {
            groupCombinations[groupIds].push({
              ...course,
            });
          }
        });

        subject = {
          ...subject,
          groupCombinations: { ...groupCombinations },
          newCourses: {
            ...this.newCourses.find(
              (courseSubject) => courseSubject.subject === subject.id,
            )?.groupCombinations,
          },
        };

        return subject;
      });
    },
    tableItems() {
      return this.items.map((subject) => {
        // eslint-disable-next-line no-unused-vars
        let { courses, groupCombinations, ...reducedSubject } = subject;
        return {
          subject: reducedSubject,
          ...Object.fromEntries(
            this.groupHeaders.map((header) => [header.value, []]),
          ),
          ...subject.groupCombinations,
          ...subject.newCourses,
        };
      });
    },
  },
  apollo: {
    currentValidityRange: {
      query: gqlCurrentValidityRange,
      result(data) {
        this.internalValidityRange = data.data.currentValidityRange;
      },
    },
    groups: {
      query: gqlGroups,
      result(data) {
        this.selectedGroups = data.data.groups;
      },
    },
    subjects: {
      query: subjects,
      skip() {
        return !this.groupIDList.length;
      },
      variables() {
        return {
          groups: this.groupIDList,
        };
      },
    },
    persons: {
      query: gqlTeachers,
    },
  },
};
</script>

<style scoped></style>
