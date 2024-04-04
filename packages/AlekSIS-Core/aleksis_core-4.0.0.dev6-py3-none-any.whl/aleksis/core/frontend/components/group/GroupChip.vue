<script>
export default {
  name: "GroupChip",
  extends: "v-chip",
  props: {
    group: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-chip
    v-bind="$attrs"
    v-on="$listeners"
    :to="{ name: 'core.group', params: { id: group.id } }"
  >
    {{ group.name }}
  </v-chip>
</template>

<style scoped></style>
