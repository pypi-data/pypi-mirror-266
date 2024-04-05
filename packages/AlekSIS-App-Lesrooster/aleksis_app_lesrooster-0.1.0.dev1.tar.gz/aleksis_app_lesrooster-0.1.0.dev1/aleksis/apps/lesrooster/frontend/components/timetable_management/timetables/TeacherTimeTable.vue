<script>
import { defineComponent } from "vue";
import { lessonsTeacher } from "./timetables.graphql";
import MiniTimeTable from "./MiniTimeTable.vue";

export default defineComponent({
  name: "TeacherTimeTable",
  extends: MiniTimeTable,
  props: {
    teacherId: {
      type: String,
      required: true,
    },
  },
  computed: {
    lessons() {
      return this.lessonsTeacher;
    },
  },
  apollo: {
    lessonsTeacher: {
      query: lessonsTeacher,
      variables() {
        return {
          timeGrid: this.timeGrid.id,
          teacher: this.teacherId,
        };
      },
      skip() {
        return this.timeGrid === null;
      },
    },
  },
});
</script>
