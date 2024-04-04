<template>
  <v-form v-model="valid">
    <c-r-u-d-list
      v-bind="$attrs"
      v-on="$listeners"
      :gql-create-mutation="gqlCreateMutation"
      :get-create-data="getCreateData"
      :item-id="itemId"
      :show-create="isCreate"
      :enable-edit="false"
      :show-select="isCreate"
      :show-action-column="isCreate"
      :lock="!isCreate"
      @lastQuery="affectedQuery = $event"
      @mode="handleMode"
      @loading="handleLoading($event)"
      @items="$emit('items', $event)"
    >
      <template #filters="{ attrs, on }">
        <slot name="filters" :attrs="attrs" :on="on" />
      </template>

      <template
        v-for="header in $attrs.headers.filter((header) => !header.disableEdit)"
        #[fieldSlot(header)]="{ item, isCreate, on, attrs }"
      >
        <slot
          :name="fieldSlot(header)"
          :attrs="attrs"
          :on="on"
          :item="item"
          :is-create="isCreate"
        />
      </template>

      <template #additionalActions>
        <edit-button
          v-if="isCreate"
          @click="isCreate = false"
          :disabled="mode || loading"
        />
        <cancel-button v-if="!isCreate" @click="cancelInlineEdit" />
        <save-button
          v-if="!isCreate"
          @click="saveInlineEdit"
          :loading="loading"
          :disabled="!valid"
        />
      </template>

      <!-- Row template -->
      <template
        v-for="(header, idx) in $attrs.headers"
        #[header.value]="{ item }"
      >
        <!-- used for transition between edit and not, MAYBE broken -->
        <v-scroll-x-transition mode="out-in" :key="idx">
          <!-- Non inline editable row -->
          <!-- span for if else, key for transition -->
          <span key="value" v-if="isCreate || header.disableEdit">
            <slot :name="header.value" :item="item">{{
              item[header.value]
            }}</slot>
          </span>
          <!-- Inline editable row -->
          <span key="field" v-else>
            <slot
              :name="header.value + '.field'"
              :item="item"
              :is-create="false"
              :attrs="{
                disabled: loading,
                value: inlineEdits?.[item.id]?.[header.value]
                  ? inlineEdits[item.id][header.value]
                  : item[header.value],
                inputValue: inlineEdits?.[item.id]?.[header.value]
                  ? inlineEdits[item.id][header.value]
                  : item[header.value],
                dense: true,
                filled: true,
                hideDetails: 'auto',
              }"
              :on="buildOn(dynamicSetter(item.id, header.value))"
            >
              <!-- split the v-model -->
              <!-- assumes that value only provides initial value -->
              <!-- log input to inlineEdits -->
              <v-text-field
                filled
                dense
                hide-details="auto"
                :disabled="loading"
                :value="item[header.value]"
                @input="handleInlineEdit(item.id, header.value, $event)"
              ></v-text-field>
            </slot>
          </span>
        </v-scroll-x-transition>
      </template>

      <template #loading>
        <slot name="loading"></slot>
      </template>
      <template #no-data>
        <slot name="no-data"></slot>
      </template>
      <template #no-results>
        <slot name="no-results"></slot>
      </template>
    </c-r-u-d-list>
  </v-form>
</template>

<script>
import CRUDList from "./CRUDList.vue";
import EditButton from "./buttons/EditButton.vue";
import CancelButton from "./buttons/CancelButton.vue";
import SaveButton from "./buttons/SaveButton.vue";

import createOrPatchMixin from "../../mixins/createOrPatchMixin.js";

export default {
  name: "InlineCRUDList",
  components: {
    CRUDList,
    EditButton,
    CancelButton,
    SaveButton,
  },
  mixins: [createOrPatchMixin],
  data() {
    return {
      valid: false,
      // Modal state
      mode: false,
      // Store inline edits
      inlineEdits: {},
    };
  },
  methods: {
    handleMode(mode) {
      this.mode = mode;
      // Re-emit
      this.$emit("mode", mode);
    },
    // inline edit
    handleInlineEdit(id, prop, value) {
      if (!this.inlineEdits[id]) {
        this.$set(this.inlineEdits, id, {});
      }
      this.$set(this.inlineEdits[id], this.itemId, id);
      this.$set(this.inlineEdits[id], prop, value);
    },
    cancelInlineEdit() {
      this.inlineEdits = {};
      // Disable editing = switch to creating
      this.isCreate = true;
    },
    saveInlineEdit() {
      this.createOrPatch(Object.values(this.inlineEdits));
    },
    buildOn(setter) {
      return {
        input: setter,
        change: setter,
      };
    },
    dynamicSetter(id, fieldName) {
      return this.handleInlineEdit.bind(null, id, fieldName);
    },
    // Template names
    fieldSlot(header) {
      return header.value + ".field";
    },
  },
  mounted() {
    this.$on("save", (_data) => {
      if (this.inlineEdits) {
        this.cancelInlineEdit();
      }
    });
  },
};
</script>
