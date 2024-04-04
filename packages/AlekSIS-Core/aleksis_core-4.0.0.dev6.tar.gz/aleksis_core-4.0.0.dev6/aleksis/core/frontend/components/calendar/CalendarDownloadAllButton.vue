<script>
export default {
  name: "CalendarDownloadAllButton",
  props: {
    url: {
      type: String,
      required: true,
    },
  },
};
</script>
<template>
  <v-btn depressed block :href="url">
    <v-icon left>mdi-download-outline</v-icon>
    {{ $t("calendar.download_all") }}
  </v-btn>
</template>
