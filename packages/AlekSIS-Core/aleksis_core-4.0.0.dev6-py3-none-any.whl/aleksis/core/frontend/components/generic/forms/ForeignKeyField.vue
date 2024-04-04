<template>
  <v-autocomplete
    v-bind="$attrs"
    v-on="$listeners"
    :items="items"
    item-value="id"
    :item-text="itemName"
    class="fc-my-auto"
  >
    <template #item="item">
      <slot name="item" v-bind="item">
        {{ item.item[itemName] }}
      </slot>
    </template>
    <template #append-outer v-if="enableCreate">
      <v-btn icon @click="createMode = true">
        <v-icon>$plus</v-icon>
      </v-btn>

      <slot
        name="createComponent"
        :attrs="{
          value: createMode,
          defaultItem: $attrs['default-item'],
          gqlQuery: lastQuery,
          gqlCreateMutation: $attrs['gql-create-mutation'],
          gqlPatchMutation: $attrs['gql-patch-mutation'],
          isCreate: true,
          fields: $attrs['fields'],
          getCreateData: $attrs['getCreateData'],
          createItemI18nKey: $attrs['createItemI18nKey'],
        }"
        :on="{
          input: (i) => (createMode = i),
          save: handleSave,
        }"
      >
        <dialog-object-form
          v-model="createMode"
          @save="handleSave"
          :is-create="true"
          :default-item="$attrs['default-item']"
          :fields="$attrs['fields']"
          :gql-query="lastQuery"
          :gql-patch-mutation="$attrs['gql-patch-mutation']"
          :gql-create-mutation="$attrs['gql-create-mutation']"
          :create-item-i18n-key="$attrs['create-item-i18n-key']"
          :get-create-data="$attrs['get-create-data']"
        >
          <template
            v-for="(_, name) in $scopedSlots"
            :slot="name"
            slot-scope="slotData"
          >
            <slot :name="name" v-bind="slotData" />
          </template>
        </dialog-object-form>
      </slot>

      <closable-snackbar :color="snackbarState" v-model="snackbar">
        {{ snackbarText }}
      </closable-snackbar>
    </template>
  </v-autocomplete>
</template>

<script>
import ClosableSnackbar from "../dialogs/ClosableSnackbar.vue";
import DialogObjectForm from "../dialogs/DialogObjectForm.vue";

import queryMixin from "../../../mixins/queryMixin.js";

export default {
  name: "ForeignKeyField",
  components: { ClosableSnackbar, DialogObjectForm },
  mixins: [queryMixin],
  extends: "v-autocomplete",
  data() {
    return {
      createMode: false,
      snackbar: false,
      snackbarState: "error",
      snackbarText: "",
    };
  },
  methods: {
    handleSave(data) {
      let newItem =
        data.data[this.gqlCreateMutation.definitions[0].name.value].item;
      let newValue = "return-object" in this.$attrs ? newItem : newItem.id;
      let modelValue =
        "multiple" in this.$attrs
          ? Array.isArray(this.$attrs.value)
            ? this.$attrs.value.concat(newValue)
            : [newValue]
          : newValue;

      this.$emit("input", modelValue);
    },
    slotName(field) {
      return field.value + ".field";
    },
  },
  props: {
    itemName: {
      type: [String, Function],
      required: false,
      default: "name",
    },
    enableCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
};
</script>

<style scoped>
.fc-my-auto > :first-child {
  margin-block: auto;
}
</style>
