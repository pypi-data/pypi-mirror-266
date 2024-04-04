<template>
  <v-sheet class="mb-10">
    <!-- Create personal event button (fab) -->
    <personal-event-dialog @save="$refs.calendar.refresh()" />
    <v-row align="stretch" class="page-height flex-nowrap">
      <v-navigation-drawer
        :clipped="$vuetify.breakpoint.lgAndUp"
        hide-overlay
        disable-route-watcher
        v-model="sidebar"
        lg="3"
        xl="2"
        :floating="$vuetify.breakpoint.lgAndUp"
        class="pt-6"
        :temporary="$vuetify.breakpoint.mdAndDown"
        :app="$vuetify.breakpoint.mdAndDown"
      >
        <calendar-control-bar
          @prev="$refs.calendar.prev()"
          @next="$refs.calendar.next()"
          @today="calendarFocus = ''"
        />

        <!-- Mini date picker -->
        <v-date-picker
          @wheel.native.prevent="handleWheel"
          no-title
          v-model="calendarFocus"
          :first-day-of-week="1"
          full-width
        ></v-date-picker>

        <!-- Calendar select (only desktop) -->
        <v-list flat subheader>
          <v-subheader>
            {{ $t("calendar.my_calendars") }}
          </v-subheader>
          <calendar-select
            class="mb-4 overflow-auto"
            v-model="selectedCalendarFeedNames"
            :calendar-feeds="calendar.calendarFeeds"
            @input="storeActivatedCalendars"
          />
        </v-list>
        <template #append>
          <div class="pa-4 d-flex justify-center align-center">
            <v-spacer />
            <calendar-download-all-button
              v-if="calendar?.allFeedsUrl"
              :url="calendar.allFeedsUrl"
            />
            <v-spacer />
          </div>
        </template>
      </v-navigation-drawer>
      <v-col lg="9" xl="10" class="d-flex flex-column fill-height">
        <div class="d-flex justify-space-between flex-wrap mb-2 align-center">
          <!-- Calendar title with current calendar time range -->
          <h2 v-if="$refs.calendar">
            <v-btn
              icon
              @click="sidebar = true"
              small
              v-if="$vuetify.breakpoint.mdAndDown"
            >
              <v-icon>mdi-menu</v-icon>
            </v-btn>
            {{ $refs.calendar.title }}
          </h2>

          <!-- Control bar with prev, next and today buttons -->
          <calendar-control-bar
            v-if="$vuetify.breakpoint.mdAndDown"
            @prev="$refs.calendar.prev()"
            @next="$refs.calendar.next()"
            @today="calendarFocus = ''"
            small
          />

          <!-- Calendar type select (month, week, day) -->
          <calendar-type-select v-model="calendarType" class="mt-1 ma-md-0" />
        </div>
        <v-row class="overflow-auto calendar-height">
          <!-- Actual calendar -->
          <v-col class="fill-height">
            <calendar
              :calendar-feeds="selectedFeedsForCalendar"
              @changeCalendarFocus="setCalendarFocus"
              @changeCalendarType="setCalendarType"
              ref="calendar"
              height="100%"
              class="fill-height"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-sheet>
</template>

<script>
import { DateTime } from "luxon";

import CalendarSelect from "./CalendarSelect.vue";

import PersonalEventDialog from "./personal_event/PersonalEventDialog.vue";

import CalendarControlBar from "./CalendarControlBar.vue";
import CalendarTypeSelect from "./CalendarTypeSelect.vue";
import Calendar from "./Calendar.vue";
import CalendarDownloadAllButton from "./CalendarDownloadAllButton.vue";
import calendarMixin from "./calendarMixin";
import calendarSelectedFeedsMixin from "./calendarSelectedFeedsMixin";

export default {
  name: "CalendarOverview",
  mixins: [calendarMixin, calendarSelectedFeedsMixin],
  components: {
    Calendar,
    CalendarTypeSelect,
    CalendarControlBar,
    CalendarSelect,
    CalendarDownloadAllButton,
    PersonalEventDialog,
  },
  methods: {
    handleWheel(event) {
      if (event.wheelDelta < 0) {
        this.$refs.calendar.next();
      } else {
        this.$refs.calendar.prev();
      }
    },
  },
  computed: {
    sidebar: {
      get() {
        return this.internalSidebar || this.$vuetify.breakpoint.lgAndUp;
      },
      set(value) {
        this.internalSidebar = value;
      },
    },
  },
  data() {
    return {
      internalSidebar: false,
    };
  },
  mounted() {
    if (this.$route.name === "core.calendar_overview") {
      this.setCalendarFocus(DateTime.now().toISODate());
      this.setCalendarType(this.$vuetify.breakpoint.mdAndDown ? "day" : "week");
    } else {
      // If we are here, we have a date supplied via the route params
      this.setCalendarFocus(
        [
          this.$route.params.year,
          this.$route.params.month,
          this.$route.params.day,
        ].join("-"),
      );
      this.setCalendarType(this.$route.params.view);
    }
  },
  watch: {
    calendarFocus(newValue, oldValue) {
      // Do not redirect on first page load
      if (oldValue === "") return;

      const [year, month, day] = newValue.split("-");
      this.$router.push({
        name: "core.calendar_overview_with_params",
        params: {
          view: this.calendarType,
          year,
          month,
          day,
        },
      });
    },
    calendarType(newValue) {
      const [year, month, day] = this.calendarFocus.split("-");
      this.$router.push({
        name: "core.calendar_overview_with_params",
        params: {
          view: newValue,
          year,
          month,
          day,
        },
      });
    },
  },
};
</script>

<style scoped>
.page-height {
  /* not all browsers support dvh so we use vh as fallback */
  height: calc(98vh - 12rem);
  height: calc(100dvh - 12rem);
  overflow: auto;
}

.calendar-height {
  min-height: 400px;
}
</style>
