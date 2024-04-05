<script>
import { defineComponent } from "vue";
import { timeGrids } from "./validityRange.graphql";
import ConfirmDialog from "aleksis.core/components/generic/dialogs/ConfirmDialog.vue";
import PrimaryActionButton from "aleksis.core/components/generic/buttons/PrimaryActionButton.vue";

export default defineComponent({
  name: "CopyFromTimeGridMenu",
  components: { ConfirmDialog, PrimaryActionButton },
  apollo: {
    timeGrids: {
      query: timeGrids,
      variables() {
        return {
          filters: JSON.stringify({
            group: this.groupMatch,
          }),
          orderBy: ["validity_range__date_start", "validity_range__date_end"],
        };
      },
      update: (data) => data.items,
    },
  },
  computed: {
    grids() {
      return this.timeGrids.filter((grid) => !this.denyIds.includes(grid.id));
    },
  },
  props: {
    groupMatch: {
      required: false,
      type: Object,
      default: undefined,
    },
    denyIds: {
      required: false,
      default: () => [],
      type: Array,
    },
  },
  data() {
    return {
      dialog: false,
      gridToCopyFrom: null,
      timeGrids: [],
    };
  },
  methods: {
    openConfirmationDialog(grid) {
      this.gridToCopyFrom = grid;
      this.dialog = true;
    },
    confirm() {
      console.log("Confirmed");
      this.$emit("confirm", this.gridToCopyFrom);
      this.dialog = false;
    },
    cancel() {
      console.log("Cancelled");
      this.dialog = false;
      this.gridToCopyFrom = null;
    },
    formatTimeGrid(item) {
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
  <div>
    <v-menu offset-y>
      <template #activator="{ attrs, on }">
        <slot name="activator" :attrs="attrs" :on="on">
          <primary-action-button
            i18n-key="actions.copy_last_configuration"
            icon="mdi-content-copy"
          />
        </slot>
      </template>
      <v-list dense>
        <v-list-item
          v-for="(grid, index) in grids"
          @click="openConfirmationDialog(grid)"
          :key="index"
        >
          <v-list-item-title>{{ formatTimeGrid(grid) }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <confirm-dialog v-model="dialog" @confirm="confirm" @cancel="cancel">
      <template #title>
        {{ $t("actions.confirm_copy_last_configuration") }}
      </template>
      <template #text>
        {{ $t("actions.confirm_copy_last_configuration_message") }}
      </template>
    </confirm-dialog>
  </div>
</template>

<style scoped></style>
