<template>
  <secondary-action-button
    v-bind="$attrs"
    v-on="$listeners"
    :i18n-key="i18nKey"
  >
    <v-icon v-if="filterIcon" left>{{ filterIcon }}</v-icon>
    <v-badge color="secondary" :value="numFilters" :content="numFilters" inline>
      <span v-t="i18nKey" />
    </v-badge>
    <v-btn
      icon
      @click.stop="$emit('clear')"
      small
      v-if="numFilters"
      class="mr-n1"
    >
      <v-icon>$clear</v-icon>
    </v-btn>
  </secondary-action-button>
</template>

<script>
import SecondaryActionButton from "./SecondaryActionButton.vue";

export default {
  name: "FilterButton",
  components: { SecondaryActionButton },
  extends: SecondaryActionButton,
  computed: {
    filterIcon() {
      return this.hasFilters || this.numFilters > 0
        ? "$filterSet"
        : "$filterEmpty";
    },
  },
  props: {
    i18nKey: {
      type: String,
      required: false,
      default: "actions.filter",
    },
    hasFilters: {
      type: Boolean,
      required: false,
      default: false,
    },
    numFilters: {
      type: Number,
      required: false,
      default: 0,
    },
  },
};
</script>
