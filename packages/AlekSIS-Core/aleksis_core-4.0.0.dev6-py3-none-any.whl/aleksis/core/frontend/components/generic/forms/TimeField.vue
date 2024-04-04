<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    offset-y
    min-width="290"
    eager
  >
    <template #activator="{ on, attrs }">
      <v-text-field
        v-model="time"
        v-bind="{ ...$attrs, ...attrs }"
        @click="handleClick"
        @focusin="handleFocusIn"
        @focusout="handleFocusOut"
        @click:clear="handleClickClear"
        placeholder="HH:MM[:SS]"
        @keydown.esc="menu = false"
        @keydown.enter="menu = false"
        :prepend-icon="prependIcon"
        :rules="mergedRules"
      ></v-text-field>
    </template>
    <v-time-picker
      v-model="time"
      ref="picker"
      :min="min"
      :max="max"
      full-width
      format="24hr"
      @click:minute="menu = false"
    ></v-time-picker>
  </v-menu>
</template>

<script>
export default {
  name: "TimeField",
  extends: "v-text-field",
  data() {
    return {
      menu: false,
      innerTime: this.value,
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
    prependIcon: {
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
    time: {
      get() {
        return this.innerTime;
      },
      set(value) {
        this.innerTime = value;
        this.$emit("input", value);
      },
    },
    mergedRules() {
      return [
        (v) =>
          !v ||
          /^([01]\d|2[0-3]):([0-5]\d)(:([0-5]\d))?$/.test(v) ||
          this.$t("forms.errors.invalid_time"),
        ...this.rules,
      ];
    },
  },
  methods: {
    handleClickClear() {
      if (this.clearable) {
        this.time = null;
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
      this.innerTime = newValue;
    },
  },
};
</script>

<style scoped></style>
