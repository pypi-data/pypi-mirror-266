<script>
import { defineComponent } from "vue";
import { createSlots } from "../breaks_and_slots/slot.graphql";
import { createBreakSlots } from "../breaks_and_slots/break.graphql";
import CancelButton from "aleksis.core/components/generic/buttons/CancelButton.vue";
import CreateButton from "aleksis.core/components/generic/buttons/CreateButton.vue";
import MobileFullscreenDialog from "aleksis.core/components/generic/dialogs/MobileFullscreenDialog.vue";
import PositiveSmallIntegerField from "aleksis.core/components/generic/forms/PositiveSmallIntegerField.vue";
import TimeField from "aleksis.core/components/generic/forms/TimeField.vue";
import WeekDayField from "aleksis.core/components/generic/forms/WeekDayField.vue";

export default defineComponent({
  name: "SlotCreator",
  components: {
    CreateButton,
    CancelButton,
    PositiveSmallIntegerField,
    WeekDayField,
    MobileFullscreenDialog,
    TimeField,
  },
  data() {
    return {
      dialog: false,
      slots: {
        weekdays: [],
        period: null,
        timeStart: "8:00",
        timeEnd: "9:00",
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
  props: {
    timeGrid: {
      type: String,
      required: true,
    },
    breaks: {
      type: Boolean,
      required: false,
      default: false,
    },
    query: {
      type: Object,
      required: true,
    },
  },
  methods: {
    save() {
      this.loading = true;
      this.$apollo
        .mutate({
          mutation: this.breaks ? createBreakSlots : createSlots,
          variables: {
            input: this.slots.weekdays.map((weekday) => ({
              name: "",
              timeGrid: this.timeGrid,
              period: this.slots.period,
              weekday: parseInt(weekday[2]),
              timeStart: this.slots.timeStart,
              timeEnd: this.slots.timeEnd,
            })),
          },
          update: (store, data) => {
            let mutationName = this.breaks ? "createBreakSlots" : "createSlots";
            this.$emit("update", store, data.data[mutationName].items);

            let query = {
              ...this.query.options,
              variables: JSON.parse(this.query.previousVariablesJson),
            };
            // Read the data from cache for query
            const storedData = store.readQuery(query);

            if (!storedData) {
              // There are no data in the cache yet
              return;
            }

            storedData.items = [
              ...storedData.items,
              ...data.data[mutationName].items,
            ];

            // Write data back to the cache
            store.writeQuery({ ...query, data: storedData });
          },
        })
        .then((data) => {
          this.$emit("save", data);

          this.handleSuccess();
        })
        .catch((error) => {
          console.error(error);
          this.$emit("error", error);
        })
        .finally(() => {
          this.loading = false;
          this.dialog = false;
        });
    },
    handleSuccess() {
      this.$root.snackbarItems.push({
        id: crypto.randomUUID(),
        timeout: 5000,
        messageKey: `lesrooster.${
          this.breaks ? "break" : "slot"
        }.create_items_success`,
        color: "success",
      });
    },
  },
});
</script>

<template>
  <mobile-fullscreen-dialog v-model="dialog">
    <template #activator="{ on, attrs }">
      <slot name="activator" v-bind="{ on, attrs }" />
    </template>

    <template #title>
      {{ $t(`lesrooster.${breaks ? "break" : "slot"}.create_items`) }}
    </template>

    <template #content>
      <div v-if="!breaks" aria-required="true">
        <positive-small-integer-field
          v-model="slots.period"
          :label="$t('lesrooster.slot.period')"
          :rules="required"
        />
      </div>

      <div aria-required="true">
        <week-day-field
          v-model="slots.weekdays"
          multiple
          chips
          :label="$t('lesrooster.slot.weekdays')"
          :rules="required"
        />
      </div>

      <v-row>
        <v-col>
          <div aria-required="true">
            <time-field
              v-model="slots.timeStart"
              :label="$t('lesrooster.slot.time_start')"
              :rules="required"
            />
          </div>
        </v-col>

        <v-col>
          <div aria-required="true">
            <time-field
              v-model="slots.timeEnd"
              :label="$t('lesrooster.slot.time_end')"
              :rules="required"
            />
          </div>
        </v-col>
      </v-row>
    </template>

    <template #actions>
      <cancel-button @click="dialog = false" />
      <create-button @click="save" />
    </template>
  </mobile-fullscreen-dialog>
</template>

<style scoped></style>
