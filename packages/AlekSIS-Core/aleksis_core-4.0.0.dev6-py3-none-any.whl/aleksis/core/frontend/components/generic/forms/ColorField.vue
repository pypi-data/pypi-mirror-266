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
        v-model="color"
        v-bind="$attrs"
        v-on="$listeners"
        placeholder="#AABBCC"
        :rules="$rules().isHexColor(allowAlpha).build(rules)"
      >
        <template #prepend-inner>
          <v-icon :color="color" v-bind="attrs" v-on="on"> mdi-circle </v-icon>
        </template>
      </v-text-field>
    </template>
    <v-color-picker v-if="menu" v-model="color" ref="picker"></v-color-picker>
  </v-menu>
</template>

<script>
import formRulesMixin from "../../../mixins/formRulesMixin";

export default {
  name: "ColorField",
  extends: "v-text-field",
  mixins: [formRulesMixin],
  data() {
    return {
      menu: false,
    };
  },
  props: {
    value: {
      type: String,
      default: undefined,
    },
    rules: {
      type: Array,
      required: false,
      default: () => [],
    },
    allowAlpha: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  computed: {
    color: {
      get() {
        return this.value;
      },
      set(newValue) {
        this.$emit("input", newValue);
      },
    },
  },
};
</script>

<style scoped></style>
