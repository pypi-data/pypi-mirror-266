<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    offset-y
    min-width="auto"
    eager
  >
    <template #activator="{ on, attrs }">
      <v-text-field
        v-model="date"
        v-bind="{ ...$attrs, ...attrs }"
        @click="handleClick"
        @focusin="handleFocusIn"
        @focusout="handleFocusOut"
        @click:clear="handleClickClear"
        placeholder="YYYY-MM-DD"
        @keydown.esc="menu = false"
        @keydown.enter="menu = false"
        :rules="mergedRules"
      ></v-text-field>
    </template>
    <v-date-picker
      v-model="date"
      ref="picker"
      no-title
      scrollable
      :min="min"
      :max="max"
      :locale="$i18n.locale"
      first-day-of-week="1"
      show-adjacent-months
      @input="menu = false"
    ></v-date-picker>
  </v-menu>
</template>

<script>
export default {
  name: "DateField",
  extends: "v-text-field",
  data() {
    return {
      menu: false,
      innerDate: this.value,
      openDueToFocus: true,
    };
  },
  props: {
    value: {
      type: String,
      required: false,
      default: undefined,
    },
    min: {
      type: String,
      required: false,
      default: undefined,
    },
    max: {
      type: String,
      required: false,
      default: undefined,
    },
    rules: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  computed: {
    date: {
      get() {
        return this.innerDate;
      },
      set(value) {
        this.innerDate = value;
        this.$emit("input", value);
      },
    },
    mergedRules() {
      return [
        (value) =>
          !value || !!Date.parse(value) || this.$t("forms.errors.invalid_date"),
        (value) =>
          !value ||
          !this.min ||
          Date.parse(value) >= Date.parse(this.min) ||
          this.$t("forms.errors.date_too_early"),
        (value) =>
          !value ||
          !this.max ||
          Date.parse(value) <= Date.parse(this.max) ||
          this.$t("forms.errors.date_too_late"),
        ...this.rules,
      ];
    },
  },
  methods: {
    handleClickClear() {
      if (this.clearable) {
        this.date = null;
      }
    },
    handleClick() {
      this.menu = true;
      this.openDueToFocus = false;
    },
    handleFocusIn() {
      this.openDueToFocus = true;
      this.menu = true;
    },
    handleFocusOut() {
      if (this.openDueToFocus) this.menu = false;
    },
  },
  watch: {
    value(newValue) {
      this.innerDate = newValue;
    },
  },
};
</script>

<style scoped></style>
