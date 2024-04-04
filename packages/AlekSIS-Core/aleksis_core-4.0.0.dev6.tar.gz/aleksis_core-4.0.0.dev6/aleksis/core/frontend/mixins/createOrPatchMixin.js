import mutateMixin from "./mutateMixin.js";

/**
 * This mixin provides item creation or update via graphQL.
 */
export default {
  mixins: [mutateMixin],
  props: {
    // UPDATE NOTICE: This has the same props the DialogObjectForm used previously
    /**
     * If isCreate is true the save method will create the object or
     * patch it otherwise
     * @values true, false
     */
    isCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * The graphQL create mutation
     */
    gqlCreateMutation: {
      type: Object,
      required: false,
      default: undefined,
    },
    /**
     * The graphQL patch mutation
     */
    gqlPatchMutation: {
      type: Object,
      required: false,
      default: undefined,
    },
    /**
     * An optional function to transform a single object prior to creating it
     * @values function
     */
    getCreateData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
    /**
     * An optional function to transform a single object prior to patching it
     * @values function
     */
    getPatchData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
  },
  computed: {
    provideMutation() {
      return this.isCreate ? this.gqlCreateMutation : this.gqlPatchMutation;
    },
  },
  methods: {
    /**
     * Create or patch an array of items
     * Create if isCreate and patch otherwise.
     * This requires gql*Mutation and get*Data (Can use default)
     * itemId is the item's id property.
     *
     * @param {Array} items
     * @param {string} itemId
     */
    createOrPatch(items, itemId) {
      itemId = itemId || this.itemId || "id";
      this.mutate(
        this.provideMutation,
        {
          input: items.map(
            this.isCreate ? this.getCreateData : this.getPatchData,
          ),
        },
        this.handleUpdateAfterCreateOrPatch(itemId, this.isCreate),
      );
    },
    /**
     * Update the cached gqlQuery to reflect a successful create or patch
     * This is a no op if no gqlQuery was provided.
     */
    handleUpdateAfterCreateOrPatch(itemId, wasCreate) {
      return (cached, incoming) => {
        console.log("handleUpdateAfterCreateOrPatch", this.isCreate);
        if (wasCreate) {
          // Just append newly created objects
          return [...cached, ...incoming];
        } else {
          for (const object of incoming) {
            // Replace the updated objects
            const index = cached.findIndex((o) => o[itemId] === object[itemId]);
            cached[index] = object;
          }
          return cached;
        }
      };
    },
  },
};
