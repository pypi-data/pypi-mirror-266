<script>
export default {
  name: "CalendarTypeSelect",
  props: {
    value: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      innerValue: this.value,
      availableCalendarTypes: [
        {
          type: "month",
          translationKey: "calendar.month",
          icon: "mdi-calendar-month-outline",
          iconActive: "mdi-calendar-month",
        },
        {
          type: "week",
          translationKey: "calendar.week",
          icon: "mdi-calendar-week-outline",
          iconActive: "mdi-calendar-week",
        },
        {
          type: "day",
          translationKey: "calendar.day",
          icon: "mdi-calendar-today-outline",
          iconActive: "mdi-calendar-today",
        },
      ],
    };
  },
  watch: {
    value(val) {
      this.innerValue = val;
    },
    innerValue(val) {
      this.$emit("input", val);
    },
  },
  methods: {
    nameForMenu(item) {
      return this.$t(item.translationKey);
    },
  },
};
</script>

<template>
  <v-btn-toggle dense mandatory v-model="innerValue" class="mx-2">
    <v-btn
      v-for="calendarType in availableCalendarTypes"
      :value="calendarType.type"
      :key="calendarType.type"
    >
      <v-icon v-if="$vuetify.breakpoint.smAndDown">{{
        calendarType.type === innerValue
          ? calendarType.iconActive
          : calendarType.icon
      }}</v-icon>
      <span class="hidden-sm-and-down">{{ nameForMenu(calendarType) }}</span>
    </v-btn>
  </v-btn-toggle>
</template>
