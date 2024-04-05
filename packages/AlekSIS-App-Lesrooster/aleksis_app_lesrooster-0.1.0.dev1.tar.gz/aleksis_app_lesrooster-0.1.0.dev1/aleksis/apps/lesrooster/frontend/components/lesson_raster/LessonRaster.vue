<template>
  <div id="slot-container">
    <v-card class="sidebar">
      <v-navigation-drawer floating permanent>
        <v-list dense rounded>
          <time-grid-field
            solo
            rounded
            hide-details
            v-model="internalTimeGrid"
          />
          <slot-creator
            :query="$apollo.queries.items"
            :time-grid="internalTimeGrid.id"
            v-if="internalTimeGrid"
            :breaks="createBreaks"
          >
            <template #activator="{ on, attrs }">
              <v-list-item
                link
                v-bind="attrs"
                v-on="on"
                @click="createBreaks = false"
              >
                <v-list-item-icon>
                  <v-icon>$plus</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{
                    $t("lesrooster.slot.create_items")
                  }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              <v-list-item
                link
                v-bind="attrs"
                v-on="on"
                @click="createBreaks = true"
              >
                <v-list-item-icon>
                  <v-icon>$plus</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{
                    $t("lesrooster.break.create_items")
                  }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </slot-creator>

          <copy-from-time-grid-menu
            v-if="internalTimeGrid"
            :deny-ids="[internalTimeGrid.id]"
            @confirm="copyFromGrid"
          >
            <template #activator="{ on, attrs }">
              <v-list-item link v-bind="attrs" v-on="on">
                <v-list-item-icon>
                  <v-icon>mdi-content-copy</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>
                    {{ $t("actions.copy_last_configuration") }}
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </copy-from-time-grid-menu>
        </v-list>
      </v-navigation-drawer>
    </v-card>

    <v-hover
      v-for="weekday in weekdays"
      :key="'weekday-' + weekday"
      :style="{
        gridColumn: weekday,
      }"
      v-slot="{ hover }"
    >
      <v-card :loading="$apollo.queries.items.loading || loading.main">
        <v-card-title
          class="d-flex flex-wrap justify-space-between align-center fill-height"
        >
          <span class="min-height">{{ $t("weekdays." + weekday) }}</span>

          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                @click="deleteSlotsOfDay(weekday)"
                icon
                v-bind="attrs"
                v-on="on"
                v-show="hover"
              >
                <v-icon>$deleteContent</v-icon>
              </v-btn>
            </template>
            <span v-t="'actions.delete'"></span>
          </v-tooltip>

          <v-menu offset-y>
            <template #activator="{ on: menu, attrs }">
              <v-tooltip bottom>
                <template #activator="{ on: tooltip }">
                  <v-btn
                    icon
                    v-bind="attrs"
                    v-on="{ ...tooltip, ...menu }"
                    :loading="loading[weekday] || loading.main"
                    v-show="hover"
                  >
                    <v-icon>mdi-application-export</v-icon>
                  </v-btn>
                </template>
                <span v-t="'actions.copy_to_day'"></span>
              </v-tooltip>
            </template>
            <v-list>
              <v-list-item
                v-for="(item, index) in weekdays.filter(
                  (day) => day !== weekday,
                )"
                :key="index"
                link
              >
                <v-list-item-title @click="copyTo(weekday, item)">{{
                  $t("weekdays." + item)
                }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <v-btn
            v-if="canAddDay(left(weekday))"
            v-show="hover"
            color="secondary"
            fab
            dark
            small
            absolute
            left
            style="left: calc(-20px - 0.5rem)"
            @click="add(left(weekday))"
          >
            <v-icon>mdi-table-column-plus-before</v-icon>
          </v-btn>
          <v-btn
            v-if="canAddDay(right(weekday))"
            v-show="hover"
            color="secondary"
            fab
            dark
            small
            absolute
            right
            style="right: calc(-20px - 0.5rem)"
            @click="add(right(weekday))"
          >
            <v-icon>mdi-table-column-plus-after</v-icon>
          </v-btn>
        </v-card-title>
      </v-card>
    </v-hover>

    <slot-card
      v-for="slot in slots"
      :key="'slot-' + slot.id"
      :item="slot"
      :disabled="
        $apollo.queries.items.loading || loading.main || loading[slot.weekday]
      "
      @click:delete="deleteSlot"
      @click:copy="copySingularSlotTodDay($event.item, $event.weekday)"
      :weekdays="weekdays"
      :id="'#slot-' + slot.id"
    />

    <delete-dialog
      :gql-delete-mutation="deleteMutation"
      :affected-query="$apollo.queries.items"
      :items="itemsToDelete"
      v-model="deleteDialog"
    >
      <template #title>
        {{
          $t("lesrooster.slot.confirm_delete_slots", {
            day: $t("weekdays." + weekdayToDelete),
          })
        }}
      </template>

      <template #body>
        <ul class="text-body-1">
          <li v-for="item in itemsToDelete" :key="'delete-' + item.id">
            {{ $t("lesrooster." + item.model.toLowerCase() + ".repr", item) }}
          </li>
        </ul>
      </template>
    </delete-dialog>
  </div>
</template>

<script>
import {
  carryOverSlots,
  copySlotsFromGrid,
  slots,
  deleteSlots,
} from "../breaks_and_slots/slot.graphql";
import DeleteDialog from "aleksis.core/components/generic/dialogs/DeleteDialog.vue";
import CopyFromTimeGridMenu from "../validity_range/CopyFromTimeGridMenu.vue";
import SlotCard from "./SlotCard.vue";
import SlotCreator from "./SlotCreator.vue";
import TimeGridField from "../validity_range/TimeGridField.vue";

export default {
  name: "LessonRaster",
  components: {
    TimeGridField,
    CopyFromTimeGridMenu,
    SlotCreator,
    DeleteDialog,
    SlotCard,
  },
  apollo: {
    items: {
      query: slots,
      variables() {
        return {
          filters: JSON.stringify({
            time_grid: this.internalTimeGrid.id,
          }),
        };
      },
      result(data) {
        console.log(data);
        this.weekdays = Array.from(
          new Set(data.data.items.map((slot) => slot.weekday)),
        ).sort();
      },
      skip() {
        return this.internalTimeGrid === null;
      },
    },
  },
  data() {
    return {
      weekdays: [],
      internalTimeGrid: null,
      loading: {
        main: false,
      },
      gqlQuery: slots,
      deleteMutation: deleteSlots,
      deleteDialog: false,
      itemsToDelete: [],
      weekdayToDelete: "",
      createBreaks: false,
    };
  },
  computed: {
    slots() {
      return (
        [...(this.items || [])].sort(
          (a, b) =>
            parseInt(a.timeStart.replace(":", "")) -
            parseInt(b.timeStart.replace(":", "")),
        ) || []
      );
    },
    columns() {
      return (
        "[side] 256px " + this.weekdays.map((day) => `[${day}] 1fr`).join(" ")
      );
    },
  },
  methods: {
    intDay(weekday) {
      return Number.isInteger(weekday) ? weekday : parseInt(weekday[2]);
    },
    canAddDay(weekday) {
      if (!weekday) {
        return false;
      }

      return !this.weekdays.includes(weekday);
    },
    add(weekday) {
      if (!this.weekdays.includes(weekday)) {
        this.weekdays.push(weekday);
        this.weekdays.sort();
      }
    },
    right(weekday) {
      return weekday === "A_6"
        ? null
        : weekday.replace(/\d+$/, (match) => parseInt(match) + 1);
    },
    left(weekday) {
      return weekday === "A_0"
        ? null
        : weekday.replace(/\d+$/, (match) => parseInt(match) - 1);
    },
    async copyTo(src, dest) {
      this.loading[dest] = true;

      // As there is an error when deleting breaks and normal slots in one action, we delete them separately
      // FIXME NO ACtion

      let that = this;

      await this.$apollo.mutate({
        mutation: carryOverSlots,
        variables: {
          timeGrid: this.internalTimeGrid.id,
          fromDay: this.intDay(src),
          toDay: this.intDay(dest),
        },
        update(
          store,
          {
            data: {
              carryOverSlots: { result },
            },
          },
        ) {
          let query = {
            ...that.$apollo.queries.items.options,
            variables: JSON.parse(
              that.$apollo.queries.items.previousVariablesJson,
            ),
          };
          // Read the data from cache for query
          const storedData = store.readQuery(query);

          if (!storedData) {
            // There are no data in the cache yet
            return;
          }

          storedData.items = [
            ...storedData.items.filter((item) => item.weekday !== dest),
            ...result,
          ];

          // Write data back to the cache
          store.writeQuery({ ...query, data: storedData });
        },
      });

      this.weekdays = this.weekdays.sort((a, b) => a[2] - b[2]);
      this.loading[dest] = false;
    },
    async copySingularSlotTodDay(slot, day) {
      const that = this;

      this.loading[day] = true;
      this.$apollo
        .mutate({
          mutation: carryOverSlots,
          variables: {
            timeGrid: this.internalTimeGrid.id || slot.timeGrid.id,
            fromDay: this.intDay(slot.weekday),
            toDay: this.intDay(day),
            only: [slot.id],
          },
          update(
            store,
            {
              data: {
                carryOverSlots: { result },
              },
            },
          ) {
            let query = {
              ...that.$apollo.queries.items.options,
              variables: JSON.parse(
                that.$apollo.queries.items.previousVariablesJson,
              ),
            };
            // Read the data from cache for query
            const storedData = store.readQuery(query);

            if (!storedData) {
              // There are no data in the cache yet
              return;
            }

            storedData.items.push(result[0]);

            // Write data back to the cache
            store.writeQuery({ ...query, data: storedData });
          },
        })
        .then(() => {
          this.$toastSuccess();
        })
        .catch(() => {
          this.$toastError();
        })
        .finally(() => {
          this.loading[day] = false;
        });
    },
    deleteSlot(slot) {
      this.itemsToDelete = [slot];
      this.deleteDialog = true;
    },
    deleteSlotsOfDay(weekday) {
      this.itemsToDelete = this.items.filter(
        (slot) => slot.weekday === weekday,
      );
      this.weekdayToDelete = weekday;
      this.deleteDialog = true;
    },
    copyFromGrid(existingTimeGrid) {
      if (!this.internalTimeGrid || !this.internalTimeGrid.id) return;

      let that = this;
      this.loading.main = true;

      this.$apollo
        .mutate({
          mutation: copySlotsFromGrid,
          variables: {
            fromTimeGrid: existingTimeGrid.id,
            toTimeGrid: this.internalTimeGrid.id,
          },
          update(
            store,
            {
              data: {
                copySlotsFromGrid: { result, deleted },
              },
            },
          ) {
            let query = {
              ...that.$apollo.queries.items.options,
              variables: JSON.parse(
                that.$apollo.queries.items.previousVariablesJson,
              ),
            };
            // Read the data from cache for query
            const storedData = store.readQuery(query);

            if (!storedData) {
              // There are no data in the cache yet
              return;
            }

            for (const id of deleted) {
              // Remove item from stored data
              const index = storedData.items.findIndex((m) => m.id === id);
              storedData.items.splice(index, 1);
            }

            storedData.items.push(...result);

            // Write data back to the cache
            store.writeQuery({ ...query, data: storedData });
          },
        })
        .then(() => {
          this.$toastSuccess();
        })
        .catch(() => {
          this.$toastError();
        })
        .finally(() => {
          this.loading.main = false;
        });
    },
  },
};
</script>

<style scoped>
#slot-container {
  display: grid;
  grid-template-columns: v-bind(columns);
  grid-auto-rows: 1fr;
  gap: 0.7rem;
  overflow-x: scroll;
  margin: -1em;
  padding: 1em;
  grid-auto-flow: column;
}

.min-height {
  min-height: 36px;
}

.sidebar {
  position: fixed;
  z-index: 1;
}
</style>
