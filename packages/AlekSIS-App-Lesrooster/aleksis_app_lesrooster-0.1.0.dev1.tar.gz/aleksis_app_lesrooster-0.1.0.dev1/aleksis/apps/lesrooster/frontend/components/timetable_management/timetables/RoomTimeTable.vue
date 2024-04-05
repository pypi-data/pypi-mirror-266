<script>
import { defineComponent } from "vue";
import { lessonsRoom } from "./timetables.graphql";
import MiniTimeTable from "./MiniTimeTable.vue";

export default defineComponent({
  name: "RoomTimeTable",
  extends: MiniTimeTable,
  props: {
    roomId: {
      type: String,
      required: true,
    },
  },
  computed: {
    lessons() {
      return this.lessonsRoom;
    },
  },
  apollo: {
    lessonsRoom: {
      query: lessonsRoom,
      variables() {
        return {
          timeGrid: this.timeGrid.id,
          room: this.roomId,
        };
      },
      skip() {
        return this.timeGrid === null;
      },
    },
  },
});
</script>
