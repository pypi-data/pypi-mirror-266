<template>
  <v-snackbar v-bind="$attrs" v-on="$listeners">
    <slot />
    <template #action="{ attrs }">
      <v-btn v-bind="attrs" @click="close()" icon>
        <v-icon>$close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script>
export default {
  name: "ClosableSnackbar",
  extends: "v-snackbar",
  methods: {
    close() {
      this.$emit("input", false);
    },
  },
};
</script>

<style scoped></style>
