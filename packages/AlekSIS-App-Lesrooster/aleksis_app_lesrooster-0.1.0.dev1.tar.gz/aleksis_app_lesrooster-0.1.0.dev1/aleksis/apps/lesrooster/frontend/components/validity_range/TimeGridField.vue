<script setup>
import ForeignKeyField from "aleksis.core/components/generic/forms/ForeignKeyField.vue";
import ValidityRangeField from "./ValidityRangeField.vue";
</script>

<script>
import { defineComponent } from "vue";
import { timeGrids, createTimeGrids } from "./validityRange.graphql";
import { gqlGroups } from "../helper.graphql";

export default defineComponent({
  name: "TimeGridField",
  apollo: {
    groups: {
      query: gqlGroups,
    },
  },
  data() {
    return {
      headers: [
        {
          text: this.$t(
            "lesrooster.validity_range.time_grid.fields.validity_range",
          ),
          value: "validityRange",
          cols: 12,
        },
        {
          text: this.$t(
            "lesrooster.validity_range.time_grid.fields.is_generic",
          ),
          value: "isGeneric",
        },
        {
          text: this.$t("lesrooster.validity_range.time_grid.fields.group"),
          value: "group",
        },
      ],
      i18nKey: "lesrooster.validity_range.time_grid",
      gqlQuery: timeGrids,
      gqlCreateMutation: createTimeGrids,
      defaultItem: {
        isGeneric: false,
        group: null,
        validityRange: null,
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
  methods: {
    getCreateData(item) {
      return {
        group: item.group,
        validityRange: item.validityRange?.id,
      };
    },
    getPatchData(items) {},
    selectableGroups(itemModel) {
      if (itemModel.validityRange === null) return [];

      // Filter all groups, so we only take the ones that are not already used in this validityRange
      return this.groups?.filter(
        (group) =>
          !this.$refs.field.items.some(
            (timeGrid) =>
              timeGrid.validityRange.id === itemModel.validityRange?.id &&
              timeGrid.group !== null &&
              timeGrid.group.id === group.id,
          ),
      );
    },
    genericDisabled(itemModel) {
      if (itemModel.validityRange === null) return true;

      // Is there a timeGrid that has the same validityRange as we and no group?
      return this.$refs.field.items.some(
        (timeGrid) =>
          timeGrid.validityRange.id === itemModel.validityRange?.id &&
          timeGrid.group === null,
      );
    },
    formatItem(item) {
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
});
</script>

<template>
  <foreign-key-field
    v-bind="$attrs"
    v-on="$listeners"
    :fields="headers"
    create-item-i18n-key="lesrooster.validity_range.time_grid.create_long"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="{}"
    :default-item="defaultItem"
    :get-create-data="getCreateData"
    :get-patch-data="getPatchData"
    :item-name="formatItem"
    return-object
    ref="field"
  >
    <template #item="{ item }">
      {{ formatItem(item) }}
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #validityRange.field="{ attrs, on }">
      <div aria-required="true">
        <validity-range-field
          v-bind="attrs"
          v-on="on"
          :rules="required"
          required
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #isGeneric.field="{ attrs, on, item }">
      <v-switch
        v-bind="attrs"
        v-on="on"
        :disabled="genericDisabled(item)"
      ></v-switch>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #group.field="{ attrs, on, item }">
      <v-autocomplete
        :items="selectableGroups(item)"
        item-text="name"
        item-value="id"
        v-bind="attrs"
        v-on="on"
        :disabled="item.isGeneric"
        :loading="$apollo.queries.groups.loading"
      />
    </template>
  </foreign-key-field>
</template>

<style scoped></style>
