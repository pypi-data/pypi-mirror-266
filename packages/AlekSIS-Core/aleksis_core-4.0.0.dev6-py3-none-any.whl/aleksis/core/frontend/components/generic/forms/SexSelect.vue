<script>
import sexChoiceMixin from "../../../mixins/sexChoiceMixin";

export default {
  name: "SexSelect",
  extends: ["v-autocomplete"],
  mixins: [sexChoiceMixin],
};
</script>

<template>
  <v-autocomplete v-bind="$attrs" v-on="$listeners" :items="sexChoices">
    <template #selection="{ item }">
      <v-icon left>{{ item.icon }}</v-icon>
      <span>{{ item.text }}</span>
    </template>

    <template #item="{ item }">
      <v-list-item-avatar>
        <v-icon>{{ item.icon }}</v-icon>
      </v-list-item-avatar>
      <v-list-item-content>
        <v-list-item-title>{{ item.text }}</v-list-item-title>
      </v-list-item-content>
    </template>
  </v-autocomplete>
</template>
