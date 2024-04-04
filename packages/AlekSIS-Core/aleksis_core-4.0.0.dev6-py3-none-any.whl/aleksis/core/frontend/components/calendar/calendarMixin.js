/**
 * Mixin for use with adaptable components showing details for calendar feeds.
 */

const calendarMixin = {
  data() {
    return {
      calendarFocus: "",
      calendarType: "week",
    };
  },
  methods: {
    setCalendarFocus(val) {
      this.calendarFocus = val;
    },
    setCalendarType(val) {
      this.calendarType = val;
    },
  },
  watch: {
    calendarFocus(val) {
      this.$refs.calendar.setCalendarFocus(val);
    },
    calendarType(val) {
      this.$refs.calendar.setCalendarType(val);
    },
  },
};

export default calendarMixin;
