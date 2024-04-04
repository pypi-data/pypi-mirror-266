<script setup>
import DateField from "../generic/forms/DateField.vue";
</script>

<template>
  <foreign-key-field
    :gql-patch-mutation="{}"
    :gql-create-mutation="gqlCreateMutation"
    :gql-query="gqlQuery"
    :fields="fields"
    create-item-i18n-key="school_term.create_school_term"
    :default-item="defaultItem"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on }">
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
    <template #dateStart.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-field
          v-bind="attrs"
          v-on="on"
          required
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
  </foreign-key-field>
</template>

<script>
import ForeignKeyField from "../generic/forms/ForeignKeyField.vue";
import { createSchoolTerms, schoolTerms } from "./schoolTerm.graphql";

export default {
  name: "SchoolTermField",
  components: { ForeignKeyField },
  extends: [ForeignKeyField],
  data() {
    return {
      gqlQuery: schoolTerms,
      gqlCreateMutation: createSchoolTerms,
      fields: [
        {
          text: this.$t("school_term.name"),
          value: "name",
        },
        {
          text: this.$t("school_term.date_start"),
          value: "dateStart",
        },
        {
          text: this.$t("school_term.date_end"),
          value: "dateEnd",
        },
      ],
      defaultItem: {
        name: "",
        dateStart: "",
        dateEnd: "",
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
    };
  },
};
</script>

<style scoped></style>
