<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "BlockingCard",
  props: {
    color: {
      type: String,
      required: false,
      default: "error",
    },
    icon: {
      type: String,
      required: false,
      default: "mdi-close",
    },
  },
});
</script>

<template>
  <v-card
    height="100%"
    class="non-important-flex flex-column align-center justify-center"
    flat
  >
    <v-icon :color="color" large>{{ icon }}</v-icon>
    <slot />
    <v-overlay absolute :color="color" :value="true" opacity="0.12" />
  </v-card>
</template>

<style scoped>
.non-important-flex {
  display: flex;
}
</style>
