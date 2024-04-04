<template>
  <!--
    emitted when filters are updated
    @event input
    @property {object} filters
  -->
  <div>
    <filter-button
      v-bind="$attrs"
      v-on="$listeners"
      class="my-1 button-40"
      :num-filters="numFilters"
      @click="filterDialog = true"
      @clear="updateFilters({})"
    />
    <filter-dialog
      v-model="filterDialog"
      :filters="value"
      @filters="updateFilters"
    >
      <template #filters="{ attrs, on }">
        <slot name="filters" :attrs="attrs" :on="on" />
      </template>
    </filter-dialog>
  </div>
</template>

<script>
import FilterButton from "./buttons/FilterButton.vue";
import FilterDialog from "./dialogs/FilterDialog.vue";

/**
 * Combine filter button and filter dialog to a functional unit.
 * Showing the filter button in place.
 */
export default {
  name: "FilterBar",
  components: {
    FilterButton,
    FilterDialog,
  },
  props: {
    /**
     * Active filters
     * Use this to supply initial filters and receive updated filters
     * (via v-model)
     * @model
     */
    value: {
      type: Object,
      required: false,
      default: () => ({}),
    },
  },
  data() {
    return {
      numFilters: Object.keys(this.value).length,
      filterDialog: false,
    };
  },
  methods: {
    updateFilters(filters) {
      this.numFilters = Object.keys(filters).length;
      this.$emit("input", filters);
    },
  },
};
</script>

<style>
.button-40 {
  min-height: 40px;
}
</style>
