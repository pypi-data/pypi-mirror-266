<template>
  <mobile-fullscreen-dialog v-bind="$attrs" v-on="$listeners">
    <template #title>{{ $t("actions.filter") }}</template>

    <template #content>
      <form ref="form" @submit.prevent="save">
        <!-- @slot Insert a field for selecting a filter. -->
        <!-- This slot is required for the filter to work. -->
        <slot name="filters" :attrs="attrs" :on="on" />
      </form>
    </template>

    <template #actions>
      <cancel-button
        i18n-key="actions.clear_filters"
        @click="clearFilters"
      ></cancel-button>
      <save-button
        i18n-key="actions.filter"
        icon-text="$filterEmpty"
        @click="save"
      ></save-button>
    </template>
  </mobile-fullscreen-dialog>
</template>

<script>
import MobileFullscreenDialog from "./MobileFullscreenDialog.vue";
import CancelButton from "../buttons/CancelButton.vue";
import SaveButton from "../buttons/SaveButton.vue";

export default {
  name: "FilterDialog",
  components: { SaveButton, CancelButton, MobileFullscreenDialog },
  props: {
    filters: {
      type: Object,
      required: true,
    },
  },
  methods: {
    save() {
      // Drop values that are null, as we don't want to apply empty filter
      for (const key in this.filters) {
        if (key in this.filters && this.filters[key] === null) {
          // eslint-disable-next-line vue/no-mutating-props
          delete this.filters[key];
        }
      }

      this.$emit("filters", this.filters);
      this.$emit("input", false);
    },
    clearFilters() {
      this.$refs.form.reset();
      this.$emit("filters", {});
      this.$emit("input", false);
    },
    on(field) {
      return {
        // eslint-disable-next-line vue/no-mutating-props
        change: (i) => (this.filters[field] = i),
        // eslint-disable-next-line vue/no-mutating-props
        input: (i) => (this.filters[field] = i),
      };
    },
    attrs(field, defaultValue) {
      if ([null, undefined].includes(this.filters[field]) && !!defaultValue) {
        // eslint-disable-next-line vue/no-mutating-props
        this.filters[field] = defaultValue;
      }
      return {
        value: this.filters[field],
      };
    },
  },
};
</script>

<style scoped></style>
