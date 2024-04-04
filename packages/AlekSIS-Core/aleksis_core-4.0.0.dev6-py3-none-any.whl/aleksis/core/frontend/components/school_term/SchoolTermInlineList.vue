<script setup>
import InlineCRUDList from "../generic/InlineCRUDList.vue";
import DateField from "../generic/forms/DateField.vue";
</script>

<template>
  <inline-c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="school_term.create_school_term"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    enable-filter
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on, item }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" :rules="required"></v-text-field>
      </div>
    </template>

    <template #dateStart="{ item }">{{
      $d($parseISODate(item.dateStart), "short")
    }}</template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #dateStart.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-field
          v-bind="attrs"
          v-on="on"
          :rules="required"
          :max="item ? item.dateEnd : undefined"
        ></date-field>
      </div>
    </template>

    <template #dateEnd="{ item }">{{
      $d($parseISODate(item.dateEnd), "short")
    }}</template>
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

    <template #filters="{ attrs, on }">
      <date-field
        v-bind="attrs('date_end__gte')"
        v-on="on('date_end__gte')"
        :label="$t('school_term.after')"
      />

      <date-field
        v-bind="attrs('date_start__lte')"
        v-on="on('date_start__lte')"
        :label="$t('school_term.before')"
      />
    </template>
  </inline-c-r-u-d-list>
</template>

<script>
import {
  schoolTerms,
  createSchoolTerms,
  deleteSchoolTerms,
  updateSchoolTerms,
} from "./schoolTerm.graphql";

export default {
  name: "SchoolTermInlineList",
  data() {
    return {
      headers: [
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
      i18nKey: "school_term",
      gqlQuery: schoolTerms,
      gqlCreateMutation: createSchoolTerms,
      gqlPatchMutation: updateSchoolTerms,
      gqlDeleteMutation: deleteSchoolTerms,
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
