<template>
  <v-menu
    v-model="model"
    :close-on-content-click="false"
    :activator="selectedElement"
    :offset-x="calendarType !== 'day'"
    min-width="350px"
    :offset-y="calendarType === 'day'"
  >
    <v-card min-width="350px" flat v-if="selectedEvent">
      <v-toolbar :color="color || selectedEvent.color" dark dense>
        <v-toolbar-title>
          <slot name="title" :selected-event="selectedEvent">{{
            selectedEvent.name
          }}</slot>
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <slot name="badge" :selected-event="selectedEvent">
          <cancelled-calendar-status-chip
            v-if="selectedEvent.status === 'CANCELLED' && !withoutBadge"
          />
        </slot>
      </v-toolbar>
      <slot name="time" :selected-event="selectedEvent">
        <v-list-item v-if="!withoutTime">
          <v-list-item-icon>
            <v-icon color="primary">mdi-calendar-today-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>
              <span
                v-if="
                  selectedEvent.allDay &&
                  selectedEvent.startDateTime.equals(selectedEvent.endDateTime)
                "
              >
                {{ $d(selectedEvent.start, "short") }}
              </span>
              <span v-else-if="selectedEvent.allDay">
                {{ $d(selectedEvent.start, "short") }} –
                {{ $d(selectedEvent.end, "short") }}
              </span>
              <span
                v-else-if="
                  selectedEvent.startDateTime.hasSame(
                    selectedEvent.endDateTime,
                    'day',
                  )
                "
              >
                {{ $d(selectedEvent.start, "shortDateTime") }} –
                {{ $d(selectedEvent.end, "shortTime") }}
              </span>
              <span v-else>
                {{ $d(selectedEvent.start, "shortDateTime") }} –
                {{ $d(selectedEvent.end, "shortDateTime") }}
              </span>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </slot>
      <slot name="description" :selected-event="selectedEvent">
        <v-divider
          inset
          v-if="selectedEvent.description && !withoutDescription"
        />
        <v-list-item v-if="selectedEvent.description && !withoutDescription">
          <v-list-item-icon>
            <v-icon color="primary">mdi-card-text-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content style="white-space: pre-line">
            {{ selectedEvent.description }}
          </v-list-item-content>
        </v-list-item>
      </slot>
      <slot name="location">
        <v-divider inset v-if="selectedEvent?.location && !withoutLocation" />
        <v-list-item v-if="selectedEvent?.location && !withoutLocation">
          <v-list-item-icon>
            <v-icon color="primary">mdi-map-marker-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            {{ selectedEvent.location }}
          </v-list-item-content>
        </v-list-item>
      </slot>
      <slot name="actions" />
    </v-card>
  </v-menu>
</template>

<script>
import calendarFeedDetailsMixin from "../../mixins/calendarFeedDetails.js";
import CancelledCalendarStatusChip from "./CancelledCalendarStatusChip.vue";

export default {
  name: "BaseCalendarFeedDetails",
  components: { CancelledCalendarStatusChip },
  mixins: [calendarFeedDetailsMixin],
};
</script>
