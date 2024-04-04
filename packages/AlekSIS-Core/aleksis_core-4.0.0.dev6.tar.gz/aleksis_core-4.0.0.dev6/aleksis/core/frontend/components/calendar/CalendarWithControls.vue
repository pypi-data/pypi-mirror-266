<template>
  <div>
    <div
      class="mx-2 mb-2 text-center"
      v-if="$refs.calendar && $vuetify.breakpoint.smAndDown"
    >
      {{ $refs.calendar.title }}
    </div>

    <div class="d-flex mb-3 justify-space-between">
      <!-- Control bar with prev, next and today buttons -->
      <calendar-control-bar
        @prev="$refs.calendar.prev()"
        @next="$refs.calendar.next()"
        @today="calendarFocus = ''"
      />

      <!-- Calendar title with current calendar time range -->
      <div class="mx-2" v-if="$refs.calendar && $vuetify.breakpoint.mdAndUp">
        {{ $refs.calendar.title }}
      </div>

      <calendar-type-select v-model="calendarType" />
    </div>

    <!-- Actual calendar -->
    <calendar
      :calendar-feeds="calendarFeeds"
      @changeCalendarFocus="setCalendarFocus"
      @changeCalendarType="setCalendarType"
      v-bind="$attrs"
      ref="calendar"
      :start-with-first-time="startWithFirstTime"
    />
  </div>
</template>

<script>
import CalendarControlBar from "./CalendarControlBar.vue";
import CalendarTypeSelect from "./CalendarTypeSelect.vue";
import Calendar from "./Calendar.vue";
import calendarMixin from "./calendarMixin";
export default {
  name: "CalendarWithControls",
  components: {
    Calendar,
    CalendarTypeSelect,
    CalendarControlBar,
  },
  mixins: [calendarMixin],
  props: {
    calendarFeeds: {
      type: Array,
      required: true,
    },
    startWithFirstTime: {
      type: Boolean,
      required: false,
      default: () => true,
    },
  },
};
</script>
