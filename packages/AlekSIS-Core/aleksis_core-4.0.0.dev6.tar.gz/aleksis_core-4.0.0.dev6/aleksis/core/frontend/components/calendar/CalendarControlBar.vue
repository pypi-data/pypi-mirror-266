<script>
export default {
  name: "CalendarControlBar",
  emits: ["prev", "next", "today"],
  props: {
    small: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
};
</script>

<template>
  <div class="d-flex justify-center mx-2">
    <v-btn icon @click="$emit('prev')" :small="small">
      <v-icon>mdi-chevron-left</v-icon>
    </v-btn>
    <v-btn outlined text class="mx-1" @click="$emit('today')" :small="small">
      {{ $t("calendar.today") }}
    </v-btn>
    <v-btn icon @click="$emit('next')" :small="small">
      <v-icon>mdi-chevron-right</v-icon>
    </v-btn>
  </div>
</template>
