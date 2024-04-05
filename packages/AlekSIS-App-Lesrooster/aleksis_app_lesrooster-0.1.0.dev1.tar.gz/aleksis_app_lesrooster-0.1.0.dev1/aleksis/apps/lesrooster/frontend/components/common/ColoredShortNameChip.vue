<script>
// a color and if it needs white text
// Colors based on https://sashamaps.net/docs/resources/20-colors/
const colors = [
  ["#e6194b", true],
  ["#3cb44b", true],
  ["#ffe119", false],
  ["#4363d8", true],
  ["#f58231", true],
  ["#911eb4", true],
  ["#42d4f4", false],
  ["#f032e6", true],
  ["#bfef45", false],
  ["#fabed4", false],
  ["#469990", true],
  ["#dcbeff", false],
  ["#9a6324", true],
  ["#fffac8", false],
  ["#800000", true],
  ["#aaffc3", false],
  ["#808000", true],
  ["#ffd8b1", false],
  ["#000075", true],
  ["#a9a9a9", true],
  ["#ffffff", true],
  ["#000000", true],
];
export default {
  name: "ColoredShortNameChip",
  props: {
    /**
     * The item that is displayed using this chip
     * Needs to be an object that has a property called `shortName`
     */
    item: {
      type: Object,
      required: true,
      default: () => ({ shortName: "..." }),
    },
    /**
     * The component uses pseudorandom coloring per default. If this behavior is disabled,
     * the color from this prop is used.
     * This prop receives an array with three values:
     * - firstly a foreground color as a string
     * - secondly a background color as a string or as a boolean (true indicates light text, false dark)
     * - the third position can be empty, it is a boolean, that, if set, controls the buttons transparency
     */
    defaultColor: {
      type: Array,
      required: false,
      // fg color, bg color, can it be transparent?
      default: () => [undefined, undefined, false],
    },
    /**
     * Whether to use the default color instead of the pseudorandom one. Defaults to false.
     */
    overrideColor: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    // Returns an integer hash based on the shortName of the supplied item
    hash() {
      return this.item.shortName
        .split("")
        .reduce(
          (hashCode, currentVal) =>
            currentVal.charCodeAt(0) +
            (hashCode << 6) +
            (hashCode << 16) -
            hashCode,
          0,
        );
    },
    light() {
      // As color[1] can be a boolean or a color
      return this.color[1] === false;
    },
    dark() {
      // As color[1] can be a boolean or a color
      return this.color[1] === true;
    },
    color() {
      return this.overrideColor
        ? this.defaultColor
        : colors[this.hash % colors.length];
    },
  },
};
</script>

<template>
  <v-btn
    v-bind="$attrs"
    v-on="$listeners"
    rounded
    small
    :dark="dark"
    :light="light"
    :color="color[0]"
    :text="color?.[2]"
  >
    {{ item.shortName }}
  </v-btn>
</template>

<style scoped></style>
