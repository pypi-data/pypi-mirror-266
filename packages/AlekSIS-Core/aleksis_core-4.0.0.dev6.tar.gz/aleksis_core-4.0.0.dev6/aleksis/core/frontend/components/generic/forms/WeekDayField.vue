<template>
  <v-autocomplete
    v-bind="$attrs"
    v-on="$listeners"
    :items="items"
    :item-value="valueKey"
  ></v-autocomplete>
</template>

<script>
export default {
  name: "WeekDayField",
  extends: "v-autocomplete",
  data() {
    return {
      items: [
        {
          value: "A_0",
          valueInt: 0,
          text: this.$t("weekdays.A_0"),
        },
        {
          value: "A_1",
          valueInt: 1,
          text: this.$t("weekdays.A_1"),
        },
        {
          value: "A_2",
          valueInt: 2,
          text: this.$t("weekdays.A_2"),
        },
        {
          value: "A_3",
          valueInt: 3,
          text: this.$t("weekdays.A_3"),
        },
        {
          value: "A_4",
          valueInt: 4,
          text: this.$t("weekdays.A_4"),
        },
        {
          value: "A_5",
          valueInt: 5,
          text: this.$t("weekdays.A_5"),
        },
        {
          value: "A_6",
          valueInt: 6,
          text: this.$t("weekdays.A_6"),
        },
      ],
    };
  },
  props: {
    returnInt: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  computed: {
    valueKey() {
      return this.returnInt ? "valueInt" : "value";
    },
  },
};
</script>
