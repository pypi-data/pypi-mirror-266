<template>
  <base-calendar-feed-details v-bind="$props">
    <template #description="{ selectedEvent }">
      <v-divider
        inset
        v-if="selectedEvent.description && !withoutDescription"
      />

      <!--
        Description of the personal event
      -->
      <v-list-item v-if="selectedEvent.description && !withoutDescription">
        <v-list-item-icon>
          <v-icon color="primary">mdi-card-text-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content style="white-space: pre-line">
          {{ selectedEvent.description }}
        </v-list-item-content>
      </v-list-item>
      <v-divider inset />

      <!--
        Linked groups of the personal event
      -->
      <v-list-item v-if="selectedEvent.meta.groups.length">
        <v-list-item-icon>
          <v-icon color="primary">mdi-account-group-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            <v-chip
              v-for="group in selectedEvent.meta.groups"
              :key="group.id"
              label
              outlined
              >{{ group.name }}</v-chip
            >
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <!--
        Owner of the personal event
      -->
      <v-list-item>
        <v-list-item-icon>
          <v-icon color="primary">mdi-account-edit-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            <v-chip label outlined>{{
              selectedEvent.meta.owner.full_name
            }}</v-chip>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <!--
        Linked persons of the personal event
      -->
      <v-list-item v-if="selectedEvent.meta.persons.length">
        <v-list-item-icon>
          <v-icon color="primary">mdi-account-outline </v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            <v-chip
              v-for="person in selectedEvent.meta.persons"
              :key="person.id"
              label
              outlined
              >{{ person.full_name }}</v-chip
            >
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>

    <!--
      Actions that can be performed on the personal event.
      Only shown when the respective permissions are present.
    -->
    <template
      v-if="selectedEvent.meta.can_edit || selectedEvent.meta.can_delete"
      #actions
    >
      <v-divider inset />
      <v-card-actions>
        <!--
          Dialog with button to edit the personal event.
        -->
        <personal-event-dialog
          v-if="selectedEvent.meta.can_edit"
          :edit-item="initPatchData"
          @save="updateOnSave()"
        />

        <!--
          Dialog with button to delete the personal event.
        -->
        <delete-button
          v-if="selectedEvent.meta.can_delete"
          @click="deleteDialog = true"
          class="ml-2"
          color="error"
          text
        />
        <delete-dialog
          v-if="selectedEvent.meta.can_delete"
          :items="[{ id: selectedEvent.meta.id, name: selectedEvent.name }]"
          :gql-delete-mutation="deleteMutation"
          v-model="deleteDialog"
          @save="updateOnSave()"
        />
      </v-card-actions>
    </template>
  </base-calendar-feed-details>
</template>

<script>
import calendarFeedDetailsMixin from "../../../mixins/calendarFeedDetails.js";
import BaseCalendarFeedDetails from "../../calendar/BaseCalendarFeedDetails.vue";

import PersonalEventDialog from "../../calendar/personal_event/PersonalEventDialog.vue";
import { deletePersonalEvents } from "../../calendar/personal_event/personalEvent.graphql";

import DeleteButton from "../../generic/buttons/DeleteButton.vue";
import DeleteDialog from "../../generic/dialogs/DeleteDialog.vue";

export default {
  name: "CustomDetails",
  components: {
    BaseCalendarFeedDetails,
    PersonalEventDialog,
    DeleteButton,
    DeleteDialog,
  },
  mixins: [calendarFeedDetailsMixin],
  data() {
    return {
      deleteDialog: false,
      deleteMutation: deletePersonalEvents,
    };
  },
  emits: ["refreshCalendar"],
  methods: {
    updateOnSave() {
      this.$emit("refreshCalendar");
      this.model = false;
    },
  },
  computed: {
    initPatchData() {
      return {
        id: this.selectedEvent.meta.id,
        persons: this.selectedEvent.meta.persons.map((p) => p.id.toString()),
        groups: this.selectedEvent.meta.groups.map((g) => g.id.toString()),
        title: this.selectedEvent.name,
        description: this.selectedEvent.meta.description,
        location: this.selectedEvent.location,
        datetimeStart: this.selectedEvent.startDateTime.toISO(),
        datetimeEnd: this.selectedEvent.endDateTime.toISO(),
        dateStart: this.selectedEvent.startDateTime.toISODate(),
        dateEnd: this.selectedEvent.endDateTime.toISODate(),
        fullDay: this.selectedEvent.allDay,
        recurrences: this.selectedEvent.meta.recurrences,
        recurring: !!this.selectedEvent.meta.recurrences,
      };
    },
  },
};
</script>
