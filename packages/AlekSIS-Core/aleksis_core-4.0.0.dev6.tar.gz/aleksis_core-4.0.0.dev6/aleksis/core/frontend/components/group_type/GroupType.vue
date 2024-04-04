<script>
import CRUDList from "../generic/CRUDList.vue";

import {
  groupTypes,
  createGroupTypes,
  deleteGroupTypes,
  updateGroupTypes,
} from "./groupType.graphql";
import formRulesMixin from "../../mixins/formRulesMixin";

export default {
  name: "GroupType",
  components: { CRUDList },
  mixins: [formRulesMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("group.group_type.name"),
          value: "name",
        },
        {
          text: this.$t("group.group_type.description"),
          value: "description",
        },
      ],
      i18nKey: "group.group_type",
      gqlQuery: groupTypes,
      gqlCreateMutation: createGroupTypes,
      gqlPatchMutation: updateGroupTypes,
      gqlDeleteMutation: deleteGroupTypes,
      defaultItem: {
        name: "",
        description: "",
      },
    };
  },
  methods: {
    getData({ id, name, description }) {
      return {
        id,
        name,
        description,
      };
    },
  },
};
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="group.group_type.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :get-create-data="getData"
    :get-patch-data="getData"
    :default-item="defaultItem"
    :enable-edit="true"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on, isCreate }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="$rules().required.build()"
        ></v-text-field>
      </div>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #description.field="{ attrs, on, isCreate }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="$rules().required.build()"
        ></v-text-field>
      </div>
    </template>
  </c-r-u-d-list>
</template>

<style scoped></style>
