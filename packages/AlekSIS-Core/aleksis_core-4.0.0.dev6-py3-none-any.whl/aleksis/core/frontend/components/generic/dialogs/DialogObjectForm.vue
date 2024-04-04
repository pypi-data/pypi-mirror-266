<template>
  <mobile-fullscreen-dialog v-model="dialog" max-width="500px">
    <template #activator="{ on, attrs }">
      <!-- @slot Insert component that activates the dialog-object-form -->
      <slot name="activator" v-bind="{ on, attrs }" />
    </template>

    <template #title>
      <!-- @slot The title of the dialog-object-form -->
      <slot name="title">
        <span class="text-h5">{{
          isCreate ? $t(createItemI18nKey) : $t(editItemI18nKey)
        }}</span>
      </slot>
    </template>

    <template #content>
      <v-form v-model="valid">
        <v-container>
          <v-row>
            <v-col
              cols="12"
              :sm="field.cols || 6"
              v-for="field in fields"
              :key="field.value"
            >
              <!-- @slot Per field slot. Use #field-value.field to customize individual fields. -->
              <slot
                :label="field.text"
                :name="field.value + '.field'"
                :attrs="buildAttrs(itemModel, field)"
                :on="buildOn(dynamicSetter(itemModel, field.value))"
                :is-create="isCreate"
                :item="itemModel"
                :setter="buildExternalSetter(itemModel)"
              >
                <v-text-field
                  :label="field.text"
                  filled
                  v-model="itemModel[field.value]"
                ></v-text-field>
              </slot>
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </template>

    <template #actions>
      <cancel-button @click="cancel" :disabled="loading" />
      <save-button
        @click="createOrPatch([itemModel])"
        :loading="loading"
        :disabled="!valid"
      />
    </template>
  </mobile-fullscreen-dialog>
</template>

<script>
import createOrPatchMixin from "../../../mixins/createOrPatchMixin.js";
import SaveButton from "../buttons/SaveButton.vue";
import CancelButton from "../buttons/CancelButton.vue";
import MobileFullscreenDialog from "./MobileFullscreenDialog.vue";

/**
 * This component provides a form for creating or updating objects via graphQL (createOrPatchMixin)
 */
export default {
  name: "DialogObjectForm",
  components: {
    CancelButton,
    SaveButton,
    MobileFullscreenDialog,
  },
  mixins: [createOrPatchMixin],
  props: {
    /**
     * Dialog state (open or closed)
     * @model
     * @values true,false
     */
    value: {
      type: Boolean,
      default: false,
    },
    /**
     * Title if isCreate is true
     */
    createItemI18nKey: {
      type: String,
      required: false,
      default: "actions.create",
    },
    /**
     * Title if isCreate is false
     */
    editItemI18nKey: {
      type: String,
      required: false,
      default: "actions.edit",
    },
    /**
     * SuccessMessage if isCreate is true
     */
    createSuccessMessageI18nKey: {
      type: String,
      required: false,
      default: "status.object_create_success",
    },
    /**
     * SuccessMessage if isCreate is false
     */
    editSuccessMessageI18nKey: {
      type: String,
      required: false,
      default: "status.object_edit_success",
    },
    /**
     * Fields in dialog-object-form
     *
     * @values list of field objects
     * @example [{text: "Field text", value: "Field value name"} ...]
     */
    fields: {
      type: Array,
      required: true,
    },
    /**
     * Default item used for creation if isCreate is true
     */
    defaultItem: {
      type: Object,
      required: true,
    },
    /**
     * Default item offered for editing if isCreate is false
     */
    editItem: {
      type: Object,
      required: false,
      default: undefined,
    },
    /**
     * Update dialog from defaultItem or editItem also if dialog is shown
     * This would happen only on mount and if dialog is hidden otherwise.
     */
    forceModelItemUpdate: {
      type: Boolean,
      required: false,
      default: false,
    },
    /**
     * Also inherited props from createOrPatchMixin
     */
  },
  emits: ["cancel"],
  data() {
    return {
      valid: false,
      firstInitDone: false,
      itemModel: {},
    };
  },
  computed: {
    dialog: {
      get() {
        return this.value;
      },
      set(newValue) {
        this.$emit("input", newValue);
      },
    },
  },
  methods: {
    dynamicSetter(item, fieldName) {
      return (value) => {
        this.$set(item, fieldName, value);
      };
    },
    buildExternalSetter(item) {
      return (fieldName, value) => this.dynamicSetter(item, fieldName)(value);
    },
    buildAttrs(item, field) {
      return {
        dense: true,
        filled: true,
        value: item[field.value],
        inputValue: item[field.value],
        label: field.text,
      };
    },
    buildOn(setter) {
      return {
        input: setter,
        change: setter,
      };
    },
    cancel() {
      this.dialog = false;
      /**
       * Emitted when user cancels
       */
      this.$emit("cancel");
    },
    handleSuccess() {
      this.dialog = false;
      let snackbarTextKey = this.isCreate
        ? this.createSuccessMessageI18nKey
        : this.editSuccessMessageI18nKey;

      this.$toastSuccess(snackbarTextKey);
      this.resetModel();
    },
    resetModel() {
      this.itemModel = JSON.parse(
        JSON.stringify(this.isCreate ? this.defaultItem : this.editItem),
      );
    },
    updateModel() {
      // Only update the model if the dialog is hidden or has just been mounted
      if (this.forceModelItemUpdate || !this.firstInitDone || !this.dialog) {
        this.resetModel();
      }
    },
  },
  mounted() {
    this.$on("save", this.handleSuccess);

    this.updateModel();
    this.firstInitDone = true;

    this.$watch("isCreate", this.updateModel);
    this.$watch("defaultItem", this.updateModel, { deep: true });
    this.$watch("editItem", this.updateModel, { deep: true });
  },
};
</script>
