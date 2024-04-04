<template>
  <v-list-item-group multiple v-model="model">
    <v-list-item
      v-for="calendarFeed in calendarFeeds"
      :key="calendarFeed.name"
      :value="calendarFeed.name"
    >
      <template #default="{ active }">
        <v-list-item-action>
          <v-checkbox
            :input-value="active"
            :color="calendarFeed.color"
          ></v-checkbox>
        </v-list-item-action>

        <v-list-item-content>
          <v-list-item-title>
            {{ calendarFeed.verboseName }}
          </v-list-item-title>
        </v-list-item-content>

        <v-list-item-action>
          <v-menu bottom>
            <template #activator="{ on, attrs }">
              <v-btn fab x-small icon v-bind="attrs" v-on="on">
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list dense>
              <v-list-item :href="calendarFeed.url">
                <v-list-item-icon>
                  <v-icon>mdi-calendar-export</v-icon>
                </v-list-item-icon>
                <v-list-item-title>
                  {{ $t("calendar.download_ics") }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-list-item-action>
      </template>
    </v-list-item>
  </v-list-item-group>
</template>

<script>
export default {
  name: "CalendarSelect",
  props: {
    calendarFeeds: {
      type: Array,
      required: true,
    },
    value: {
      type: Array,
      required: true,
    },
  },
  computed: {
    model: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    someSelected() {
      return this.model.length > 0 && !this.allSelected;
    },
    allSelected() {
      return this.model.length === this.calendarFeeds.length;
    },
  },
  methods: {
    toggleAll(newValue) {
      if (newValue) {
        this.model = this.calendarFeeds.map((feed) => feed.name);
      } else {
        this.model = [];
      }
    },
  },
};
</script>
