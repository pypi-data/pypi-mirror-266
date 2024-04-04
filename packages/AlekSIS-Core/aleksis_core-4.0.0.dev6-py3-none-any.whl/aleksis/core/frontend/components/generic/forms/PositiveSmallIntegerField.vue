<template>
  <v-text-field
    v-bind="$attrs"
    v-on="on"
    :rules="
      $rules()
        .isANumber.isAWholeNumber.isGreaterThan(0)
        .isSmallerThan(32767)
        .build(rules)
    "
    type="number"
    inputmode="decimal"
  ></v-text-field>
</template>

<script>
import formRulesMixin from "../../../mixins/formRulesMixin";

export default {
  name: "PositiveSmallIntegerField",
  extends: "v-text-field",
  mixins: [formRulesMixin],
  props: {
    rules: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  computed: {
    on() {
      return {
        ...this.$listeners,
        input: this.inputHandler("input"),
        change: this.inputHandler("change"),
      };
    },
  },
  methods: {
    inputHandler(name) {
      return (event) => {
        const num = parseInt(event);
        if (!isNaN(num) && num >= 0 && num <= 32767 && num % 1 === 0) {
          this.$emit(name, num);
        }
      };
    },
  },
};
</script>

<style scoped></style>
