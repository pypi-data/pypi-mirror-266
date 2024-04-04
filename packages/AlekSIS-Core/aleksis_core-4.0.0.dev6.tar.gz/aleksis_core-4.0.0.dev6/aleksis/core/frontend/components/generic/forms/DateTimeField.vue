<script setup>
import DateField from "./DateField.vue";
import TimeField from "./TimeField.vue";
</script>

<template>
  <div>
    <v-row>
      <v-col class="py-0">
        <div>{{ $attrs.label }}</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="7">
        <date-field
          v-model="date"
          v-bind="{ ...$attrs }"
          :label="$t('forms.date_time.date')"
          :min="minDate"
          :max="maxDate"
        />
      </v-col>
      <v-col cols="5">
        <time-field
          v-model="time"
          v-bind="{ ...$attrs }"
          :label="$t('forms.date_time.time')"
          :min="minTime"
          :max="maxTime"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { DateTime } from "luxon";

export default {
  name: "DateTimeField",
  data() {
    return {
      innerDateTime: this.value,
    };
  },
  props: {
    value: {
      type: String,
      required: false,
      default: undefined,
    },
    minDate: {
      type: String,
      required: false,
      default: undefined,
    },
    maxDate: {
      type: String,
      required: false,
      default: undefined,
    },
    minTime: {
      type: String,
      required: false,
      default: undefined,
    },
    maxTime: {
      type: String,
      required: false,
      default: undefined,
    },
  },
  computed: {
    dateTime: {
      get() {
        return this.$parseISODate(this.innerDateTime);
      },
      set(value) {
        this.innerDateTime = value;
        this.$emit("input", value);
      },
    },
    date: {
      get() {
        return this.dateTime.toISODate();
      },
      set(value) {
        let newDateTime = this.dateTime;
        const date = DateTime.fromISO(value);

        newDateTime = newDateTime.set({
          year: date.year,
          month: date.month,
          day: date.day,
        });

        this.dateTime = newDateTime.toISO();
      },
    },
    time: {
      get() {
        return this.dateTime.toFormat("HH:mm");
      },
      set(value) {
        let newDateTime = this.dateTime;

        const time = DateTime.fromISO(value);

        newDateTime = newDateTime.set({ hour: time.hour, minute: time.minute });

        this.dateTime = newDateTime.toISO();
      },
    },
  },
  watch: {
    value(newValue) {
      this.innerDateTime = newValue;
    },
  },
};
</script>

<style scoped></style>
