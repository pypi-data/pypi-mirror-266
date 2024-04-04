<script>
import CRUDList from "../generic/CRUDList.vue";

import { deletePersons, persons } from "./personList.graphql";
import CreateButton from "../generic/buttons/CreateButton.vue";
import SexSelect from "../generic/forms/SexSelect.vue";
import GroupChip from "../group/GroupChip.vue";
import TableLink from "../generic/TableLink.vue";

export default {
  name: "Person",
  components: { TableLink, GroupChip, SexSelect, CreateButton, CRUDList },
  data() {
    return {
      headers: [
        {
          text: this.$t("person.first_name"),
          value: "firstName",
        },
        {
          text: this.$t("person.last_name"),
          value: "lastName",
        },
        {
          text: this.$t("person.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("person.primary_group"),
          value: "primaryGroup",
        },
      ],
      i18nKey: "person",
      gqlQuery: persons,
      gqlDeleteMutation: deletePersons,
    };
  },
};
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    :gql-query="gqlQuery"
    :gql-delete-mutation="gqlDeleteMutation"
    :enable-filter="true"
    item-attribute="fullName"
  >
    <template #createComponent>
      <create-button :to="{ name: 'core.createPerson' }" />
    </template>

    <template #filters="{ attrs, on }">
      <v-text-field
        v-bind="attrs('name')"
        v-on="on('name')"
        :label="$t('person.name')"
      />
      <v-text-field
        v-bind="attrs('contact')"
        v-on="on('contact')"
        :label="$t('person.details')"
      />
      <sex-select
        v-bind="attrs('sex')"
        v-on="on('sex')"
        :label="$t('person.sex.field')"
      />
    </template>

    <template #lastName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.lastName }}
      </table-link>
    </template>

    <template #firstName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.firstName }}
      </table-link>
    </template>

    <template #shortName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.shortName }}
      </table-link>
    </template>

    <template #primaryGroup="{ item }">
      <group-chip :group="item.primaryGroup" v-if="item.primaryGroup" />
      <span v-else>–</span>
    </template>
  </c-r-u-d-list>
</template>
