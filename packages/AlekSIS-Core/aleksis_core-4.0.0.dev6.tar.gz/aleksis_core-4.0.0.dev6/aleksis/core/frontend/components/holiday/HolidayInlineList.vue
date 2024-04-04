<script setup>
import InlineCRUDList from "../generic/InlineCRUDList.vue";
import DateField from "../generic/forms/DateField.vue";
</script>

<template>
  <inline-c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="holidays.create_holiday"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    item-attribute="holidayName"
    ref="crudList"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #holidayName.field="{ attrs, on, isCreate }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="required"
        ></v-text-field>
      </div>
    </template>

    <template #dateStart="{ item }">
      {{ $d($parseISODate(item.dateStart), "short") }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #dateStart.field="{ attrs, on, item, isCreate }">
      <div aria-required="true">
        <date-field
          v-bind="attrs"
          v-on="on"
          :rules="required"
          :max="item ? item.dateEnd : undefined"
        ></date-field>
      </div>
    </template>

    <template #dateEnd="{ item }">
      {{ $d($parseISODate(item.dateEnd), "short") }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #dateEnd.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="required"
          :min="item ? item.dateStart : undefined"
        ></date-field>
      </div>
    </template>
  </inline-c-r-u-d-list>
</template>

<script>
import {
  holidays,
  createHolidays,
  deleteHolidays,
  updateHolidays,
} from "./holiday.graphql";

export default {
  name: "HolidayInlineList",
  data() {
    return {
      headers: [
        {
          text: this.$t("holidays.holiday_name"),
          value: "holidayName",
        },
        {
          text: this.$t("holidays.date_start"),
          value: "dateStart",
        },
        {
          text: this.$t("holidays.date_end"),
          value: "dateEnd",
        },
      ],
      i18nKey: "holidays",
      gqlQuery: holidays,
      gqlCreateMutation: createHolidays,
      gqlPatchMutation: updateHolidays,
      gqlDeleteMutation: deleteHolidays,
      defaultItem: {
        holidayName: "",
        dateStart: null,
        dateEnd: null,
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
};
</script>

<style scoped></style>
