<script>
import {
  breakSlots,
  createBreakSlots,
  deleteBreakSlots,
  updateBreakSlots,
} from "./break.graphql";
import LesroosterSlot from "./LesroosterSlot.vue";

export default {
  name: "Break",
  extends: LesroosterSlot,
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
          text: this.$t("lesrooster.slot.time_start"),
          value: "timeStart",
        },
        {
          text: this.$t("lesrooster.slot.time_end"),
          value: "timeEnd",
        },
      ],
      i18nKey: "lesrooster.break",
      createItemI18nKey: "lesrooster.break.create_item",
      gqlQuery: breakSlots,
      gqlCreateMutation: createBreakSlots,
      gqlPatchMutation: updateBreakSlots,
      gqlDeleteMutation: deleteBreakSlots,
    };
  },
  methods: {
    getCreateData(item) {
      return {
        ...item,
        period: null,
        weekday: this.weekdayAsInt(item.weekday),
        timeGrid: item.timeGrid.id,
      };
    },
    getPatchData(item) {
      item = {
        id: item.id,
        name: item.name,
        weekday: item.weekday ? this.weekdayAsInt(item.weekday) : undefined,
        period: null,
        timeStart: item.timeStart,
        timeEnd: item.timeEnd,
        timeGrid: item.timeGrid?.id,
      };
      return Object.fromEntries(
        Object.entries(item).filter(([key, value]) => value !== undefined),
      );
    },
  },
};
</script>

<style scoped></style>
