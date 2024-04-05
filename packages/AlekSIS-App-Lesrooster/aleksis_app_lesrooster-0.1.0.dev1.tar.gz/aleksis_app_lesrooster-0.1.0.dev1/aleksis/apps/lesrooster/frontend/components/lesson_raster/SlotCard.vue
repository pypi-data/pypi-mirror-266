<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "SlotCard",
  props: {
    item: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
      required: false,
    },
    weekdays: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  methods: {
    handleDelete() {
      this.$emit("click:delete", this.item);
    },
    handleCopy(weekday) {
      this.$emit("click:copy", { item: this.item, weekday: weekday });
    },
  },
});
</script>

<template>
  <v-card
    :style="{
      gridColumn: item.weekday,
    }"
    :disabled="disabled"
  >
    <v-hover v-slot="{ hover }">
      <v-card-text class="d-flex align-center">
        <v-col cols="4" class="text-h4">
          <span v-if="item.model === 'Slot'">{{ item.period }}</span>
          <v-icon v-else>mdi-timer-sand-paused</v-icon>
        </v-col>

        <v-col cols="6">
          <div class="time">
            {{ $d(new Date("1970-01-01T" + item.timeStart), "shortTime") }}
          </div>
          <div class="time">
            {{ $d(new Date("1970-01-01T" + item.timeEnd), "shortTime") }}
          </div>
        </v-col>

        <v-col
          cols="2"
          class="d-flex flex-column align-center pa-0 my-n1 hover-box"
        >
          <v-tooltip left>
            <template #activator="{ on, attrs }">
              <v-btn
                icon
                v-bind="attrs"
                v-on="on"
                @click="handleDelete"
                v-show="hover"
              >
                <v-icon>$deleteContent</v-icon>
              </v-btn>
            </template>
            <span v-t="'actions.delete'"></span>
          </v-tooltip>

          <v-menu offset-y>
            <template #activator="{ on: menu, attrs }">
              <v-tooltip left>
                <template #activator="{ on: tooltip }">
                  <v-btn
                    icon
                    v-bind="attrs"
                    v-on="{ ...tooltip, ...menu }"
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
                v-for="(weekday, index) in weekdays.filter(
                  (day) => day !== item.weekday,
                )"
                :key="index"
                link
              >
                <v-list-item-title @click="handleCopy(weekday)"
                  >{{ $t("weekdays." + weekday) }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-card-text>
    </v-hover>
  </v-card>
</template>

<style scoped>
.time {
  white-space: nowrap;
}

.hover-box {
  padding-inline-end: 0.5em !important;
  min-width: calc(36px + 0.5em);
}
</style>
