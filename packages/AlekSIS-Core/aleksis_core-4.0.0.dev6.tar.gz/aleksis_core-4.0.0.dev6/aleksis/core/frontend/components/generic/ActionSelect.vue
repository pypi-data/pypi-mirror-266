<!-- MAYBE: Better name OR better place? -->
<!-- Moved out of InlineCRUDList -->
<template>
  <v-autocomplete
    auto-select-first
    clearable
    :items="actions"
    v-model="selectedAction"
    return-object
    :label="$t('actions.select_action')"
    item-text="name"
    outlined
    dense
    :hint="$tc('selection.num_items_selected', selection.length)"
    persistent-hint
    :append-outer-icon="disabled || !selectedAction ? '' : '$send'"
    @click:append-outer="handleAction"
  >
    <template #item="{ item, attrs, on }">
      <v-list-item dense v-bind="attrs" v-on="on">
        <v-list-item-icon v-if="item.icon">
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>{{ item.name }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
/**
 * This component takes a list of actions and
 * provides a autocomplete to choose one action.
 * This action is then called on a selection.
 */
export default {
  name: "ActionSelect",
  props: {
    /**
     * The values the action acts upon
     * @model
     */
    value: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Array of action objects
     *
     * An action object has a name (string), an icon (string),
     * a predicate (function called on item),
     * a handler (function called on item array) and
     * a clearSelection toggle.
     *
     * @example [
     *            {
     *              name: "action's name",
     *              icon: "action's icon",
     *              predicate: (item) => {
     *                return true if item can be handled
     *              },
     *              handler: (items) => {
     *                do the action on array of items
     *              },
     *              clearSelection: true/false,
     *            },
     *            ...
     *          ]
     */
    actions: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Disable activating the action
     * This hides the button that triggers the action
     */
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      selectedAction: null,
    };
  },
  computed: {
    selection: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit("input", val);
      },
    },
  },
  methods: {
    handleAction() {
      if (this.selectedAction) {
        if (
          this.selectedAction.predicate &&
          !this.selection.every(this.selectedAction.predicate)
        ) {
          // TODO: proper error msg, i18n
          this.handleError("Action was called on incompatible selection");
        }

        this.selectedAction.handler(this.selection);

        if (this.selectedAction.clearSelection) {
          this.selection = [];
        }
      }
    },
  },
};
</script>
