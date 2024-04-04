<!-- This is the CRUDBar - the CRUD's core -->
<!-- It contains: -->
<!-- filter search actions -->
<!-- create/patch (create btn) del -->

<!-- It returns filtered items -->
<!-- All child components can be toggled -->
<!-- Search returns a string -->
<!-- create/patch & del are fully exposed (via ref, see CRUDList) -->

<template>
  <v-toolbar flat class="height-fit child-height-fit">
    <v-row class="flex-wrap gap align-baseline pt-4">
      <v-toolbar-title class="d-flex flex-wrap w-100 gap">
        <!-- filter-selection -->
        <filter-bar
          v-if="enableFilter"
          v-model="additionalFilters"
          :disabled="loading || lock"
        >
          <template #filters="{ attrs, on }">
            <slot name="filters" :attrs="attrs" :on="on" />
          </template>
        </filter-bar>
        <!-- search-field -->
        <div class="my-1" v-if="enableSearch">
          <!--
          Emitted when search string changes
          @event search
          @property {string} search
          -->
          <v-text-field
            :value="search"
            @input="$emit('search', $event)"
            type="search"
            clearable
            rounded
            filled
            hide-details
            single-line
            prepend-inner-icon="$search"
            dense
            outlined
            :placeholder="$t('actions.search')"
            :disabled="loading || lock"
          />
        </div>
        <!-- action-autocomplete -->
        <div
          class="my-1"
          v-if="enableActions"
          v-show="actions.length > 0 && selection.length > 0"
        >
          <!--
          Emitted when selection changes
          @event selection
          @property {array} selection
          -->
          <action-select
            :value="selection"
            @input="$emit('selection', $event)"
            :actions="actions"
            :disabled="loading || lock"
          />
        </div>
      </v-toolbar-title>
      <v-spacer class="flex-grow-0 flex-sm-grow-1 mx-n1 mx-sm-0"></v-spacer>
      <!-- @slot Insert a create (and edit) component. This defaults to DialogObjectForm. -->
      <slot
        v-if="enableCreate || enableEdit"
        name="createComponent"
        :attrs="{
          value: createMode,
          defaultItem: defaultItem,
          affectedQuery: lastQuery,
          editItem: editItem,
          isCreate: isCreate,
          fields: editableHeaders,
          getCreateData: $attrs['get-create-data'],
          gqlCreateMutation: $attrs['gql-create-mutation'],
          gqlPatchMutation: $attrs['gql-patch-mutation'],
          getPatchData: $attrs['get-patch-data'],
          createItemI18nKey: $attrs['create-item-i18n-key'],
          editItemI18nKey: $attrs['edit-item-i18n-key'],
          itemId: $attrs['item-id'],
        }"
        :on="{
          input: (i) => (i ? (createMode = true) : null),
          loading: (loading) => handleLoading(loading),
        }"
        :create-mode="createMode"
        :form-field-slot-name="fieldSlot"
        :disabled="createMode || loading || lock"
      >
        <dialog-object-form
          v-model="createMode"
          :affected-query="lastQuery"
          :get-create-data="$attrs['get-create-data']"
          :get-patch-data="$attrs['get-patch-data']"
          :default-item="defaultItem"
          :gql-create-mutation="$attrs['gql-create-mutation']"
          :edit-item="editItem"
          :gql-patch-mutation="$attrs['gql-patch-mutation']"
          :is-create="isCreate"
          :fields="editableHeaders"
          :create-item-i18n-key="$attrs['create-item-i18n-key']"
          :edited-item-i18n-key="$attrs['edit-item-i18n-key']"
          :item-id="$attrs['item-id']"
          :force-model-item-update="!isCreate"
          @loading="handleLoading($event)"
        >
          <template #activator="{ props }">
            <create-button
              v-show="showCreate"
              color="secondary"
              @click="handleCreate"
              :disabled="createMode || loading || lock"
            />
          </template>
          <template
            v-for="header in editableHeaders"
            #[fieldSlot(header)]="{ item, isCreate, on, attrs }"
          >
            <!-- @slot Create component fields slot -->
            <slot
              :name="fieldSlot(header)"
              :attrs="attrs"
              :on="on"
              :item="item"
              :is-create="isCreate"
            />
          </template>
        </dialog-object-form>
      </slot>
      <!-- @slot Insert a delete component. This defaults to DeleteDialog. -->
      <slot
        v-if="enableDelete"
        name="deleteComponent"
        :attrs="{
          value: deleteMode,
          affectedQuery: lastQuery,
          gqlDeleteMutation: $attrs['gql-delete-mutation'],
          items: itemsToDelete,
          itemId: $attrs['item-id'],
          itemAttribute: $attrs['item-attribute'],
          deleteSuccessMessageI18nKey:
            $attrs['delete-success-message-i18n-key'],
        }"
        :on="{
          input: (i) => (i ? (createMode = true) : null),
          loading: (loading) => handleLoading(loading),
        }"
        :disabled="deleteMode || loading || lock"
      >
        <delete-dialog
          v-model="deleteMode"
          :affected-query="lastQuery"
          :gql-delete-mutation="$attrs['gql-delete-mutation']"
          :items="itemsToDelete"
          :item-id="$attrs['item-id']"
          :item-attribute="$attrs['item-attribute']"
          :delete-success-message-i18n-key="
            $attrs['delete-success-message-i18n-key']
          "
          @loading="handleLoading($event)"
        />
      </slot>
      <!-- @slot Insert additional things - actions/buttons - in the table header -->
      <slot name="additionalActions" />
    </v-row>
  </v-toolbar>
</template>

<script>
import FilterBar from "./FilterBar.vue";
import ActionSelect from "./ActionSelect.vue";
import DialogObjectForm from "./dialogs/DialogObjectForm.vue";
import CreateButton from "./buttons/CreateButton.vue";
import DeleteDialog from "./dialogs/DeleteDialog.vue";

import queryMixin from "../../mixins/queryMixin.js";

export default {
  name: "CRUDBar",
  components: {
    FilterBar,
    ActionSelect,
    DialogObjectForm,
    CreateButton,
    DeleteDialog,
  },
  mixins: [queryMixin],
  props: {
    // MAYBE: Replace with titleI18nKey - It is only used for that.
    // BUT this would be a breaking change @ all callsites.
    /**
     * The i18nKey for this component.
     */
    i18nKey: {
      type: String,
      required: true,
    },
    /**
     * Lock updating the items
     * Deactivates changing the filter, search, the items themselves (create, edit, delete) and selecting actions.
     * This only prohibits the user from updating the items, props can still influence them.
     * @values true, false
     */
    lock: {
      type: Boolean,
      required: false,
      default: false,
    },
    // filter
    /**
     * Enable filtering the items
     * This lets the user choose a filter and applies it to the graphQL query.
     * @values true, false
     */
    enableFilter: {
      type: Boolean,
      required: false,
      default: false,
    },
    // search
    /**
     * Enable the search input
     * @values true, false
     */
    enableSearch: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * The (initial) search input
     */
    search: {
      type: String,
      required: false,
      default: "",
    },
    // actions
    /**
     * Enable actions
     * @values true, false
     */
    enableActions: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * The selected items the actions act uppon
     */
    selection: {
      type: Array,
      required: false,
      default: () => [],
    },
    // create/patch
    /**
     * An array of objects that each describe an item field
     * This prop is a superset of the v-data-table prop with the same
     * name.
     * Used here for the create component & describes the CRUDList
     * Additional fields are documented in the example:
     *
     * @example [
     *            {
     *              // Required
     *              text: "displayed name",
     *              value: "internal name",
     *              // See v-data-table api for more.
     *              // CRUDBar specific optional fields:
     *              disableEdit: true,  // This is a non editable colum
     *              // DialogObjectForm specific optional fields:
     *              // Amount of columns used for this field
     *              // from a total of 12
     *              cols: 6,
     *              // CRUDList and CRUDIterator specific optional fields:
     *              hidden: true,       // Hide this colum
     *              orderKey: "field used for odering"
     *            },
     *            ...
     *          ]
     */
    headers: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Enable creation of items
     * via the create component (defaults to DialogObjectForm)
     * This shows a create button in the table header.
     * @values true, false
     */
    enableCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Show create button of the default create component
     * (DialogObjectForm)
     * @values true, false
     */
    showCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Default item used for creation
     * This is required if enableCreate is true and
     * the default create component slot is used.
     */
    defaultItem: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * Enable editing of items
     * via the create component (defaults to DialogObjectForm)
     * @values true, false
     */
    enableEdit: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Enable deletion of items
     * via the delete component (defaults to DeleteDialog)
     * @values true, false
     */
    enableDelete: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  emits: ["search", "selectable", "selection", "deletable", "mode"],
  data() {
    return {
      // Use create component for creation
      isCreate: true,
      // Toggle for create component
      createMode: false,
      // Used to pass item for editing
      editItem: {},
      // Show delete component
      deleteMode: false,
      // Items awaiting deletion
      itemsToDelete: [],
    };
  },
  computed: {
    deletionPossible() {
      if (
        this.enableDelete &&
        this.items &&
        this.items.some((i) => i.canDelete) &&
        this.$attrs["gql-delete-mutation"]
      ) {
        /**
         * emitted when there are items that can be deleted
         * @event deletable
         */
        this.$emit("deletable");

        return true;
      }
      return false;
    },
    // Add delete action if multiple deletion is possible
    actions() {
      const actions = this.$attrs.actions
        ? this.$attrs.actions
        : [].concat(
            this.deletionPossible
              ? [
                  {
                    name: this.$t("actions.delete"),
                    icon: "$deleteContent",
                    predicate: (item) => item.canDelete,
                    handler: (items) => {
                      this.itemsToDelete = items;
                      this.deleteMode = true;
                    },
                    clearSelection: true,
                  },
                ]
              : [],
          );
      if (actions.length > 0) {
        /**
         * emitted when there are actions to act on selection
         * @event selectable
         */
        this.$emit("selectable");
      }
      return actions;
    },
    editableHeaders() {
      return this.headers.filter((header) => !header.disableEdit);
    },
  },
  methods: {
    // actions & selectable items
    isActionableItem(item) {
      return this.actions.some((action) => action.predicate?.(item));
    },
    handleItems(items) {
      // overwrites the one in queryMixin
      return items.map((item) => {
        return { selectable: this.isActionableItem(item), ...item };
      });
    },
    // CRUD menus
    handleCreate() {
      this.isCreate = true;
      this.createMode = true;
    },
    handleEdit(item) {
      this.editItem = item;
      this.isCreate = false;
      this.createMode = true;
    },
    handleDelete(item) {
      this.itemsToDelete = [item];
      this.deleteMode = true;
    },
    // Template names
    fieldSlot(header) {
      return header.value + ".field";
    },
    // mode
    handleMode() {
      /**
       * Emitted to indicate modal dialog status
       *
       * @property {boolean} mode if true there is a modal dialog open and false if otherwise
       */
      this.$emit("mode", this.createMode || this.deleteMode);
    },
  },
  mounted() {
    this.$setToolBarTitle(this.$t(`${this.i18nKey}.title_plural`), null);

    this.$watch("createMode", this.handleMode);
    this.$watch("deleteMode", this.handleMode);
  },
};
</script>

<style>
.gap {
  gap: 0.5rem;
}
.height-fit,
.child-height-fit > * {
  height: fit-content !important;
}
</style>
