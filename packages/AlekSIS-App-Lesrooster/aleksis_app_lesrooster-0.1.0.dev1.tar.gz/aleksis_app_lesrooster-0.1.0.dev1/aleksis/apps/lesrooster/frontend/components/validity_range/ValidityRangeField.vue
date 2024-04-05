<script setup>
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
import DateField from "aleksis.core/components/generic/forms/DateField.vue";
import SchoolTermField from "aleksis.core/components/school_term/SchoolTermField.vue";
</script>

<template>
  <foreign-key-field
    v-bind="$attrs"
    v-on="$listeners"
    :fields="headers"
    create-item-i18n-key="lesrooster.validity_range.create_validity_range"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="{}"
    :default-item="defaultItem"
    :get-create-data="getCreateData"
    :get-patch-data="getPatchData"
    return-object
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #schoolTerm.field="{ attrs, on }">
      <div aria-required="true">
        <school-term-field
          v-bind="attrs"
          v-on="on"
          return-object
          :rules="required"
          required
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #dateStart.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-field
          v-bind="attrs"
          v-on="on"
          :rules="required"
          :max="item ? item.dateEnd : undefined"
        ></date-field>
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #dateEnd.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="required"
          :min="item ? item.dateStart : undefined"
        ></date-field>
      </div>
    </template>
  </foreign-key-field>
</template>

<script>
import { validityRanges, createValidityRanges } from "./validityRange.graphql";

export default {
  name: "ValidityRangeField",
  data() {
    return {
      headers: [
        {
          text: this.$t("lesrooster.validity_range.name"),
          value: "name",
        },
        {
          text: this.$t("school_term.title"),
          value: "schoolTerm",
        },
        {
          text: this.$t("lesrooster.validity_range.date_start"),
          value: "dateStart",
        },
        {
          text: this.$t("lesrooster.validity_range.date_end"),
          value: "dateEnd",
        },
      ],
      i18nKey: "lesrooster.validity_range",
      gqlQuery: validityRanges,
      gqlCreateMutation: createValidityRanges,
      defaultItem: {
        name: "",
        dateStart: "",
        dateEnd: "",
        schoolTerm: "",
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
  methods: {
    getCreateData(item) {
      return {
        ...item,
        schoolTerm: item.schoolTerm?.id,
      };
    },
    getPatchData(item) {
      item = {
        id: item.id,
        name: item.name,
        dateStart: item.dateStart,
        dateEnd: item.dateEnd,
        schoolTerm: item.schoolTerm.id,
      };
      return Object.fromEntries(
        Object.entries(item).filter(([key, value]) => value !== undefined),
      );
    },
  },
};
</script>

<style scoped></style>
