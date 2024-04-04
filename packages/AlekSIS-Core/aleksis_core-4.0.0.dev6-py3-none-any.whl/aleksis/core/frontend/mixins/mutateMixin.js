import loadingMixin from "./loadingMixin.js";

/**
 * This mixin provides generic graphQL mutation handling.
 */
export default {
  mixins: [loadingMixin],
  props: {
    /**
     * The graphQL query this mutation affects.
     * If provided the cached query will be updated.
     * Either use lastQuery from the queryMixin or
     * $apollo.queries[lastQueryName].
     */
    affectedQuery: {
      type: Object,
      required: false,
      default: null,
    },
    // itemId is unused in mutateMixin but shared by both
    // createOrPatchMixin & deleteMixin
    /**
     * The item's id property.
     */
    itemId: {
      type: String,
      required: false,
      default: "id",
    },
  },
  // update & save come from DialogObjectForm
  // save could be success as well but keeping it backwards compatible
  // for now
  emits: ["update", "save"],
  computed: {
    // Expand the affectedQuery
    expandedQuery() {
      if (!this.affectedQuery) {
        return false;
      }
      return {
        ...this.affectedQuery.options,
        variables: JSON.parse(this.affectedQuery.previousVariablesJson),
      };
    },
  },
  methods: {
    /**
     * Do a graphQL mutation with variables
     *
     * Provide updateStore to update the cached data for affectedQuery with
     * the incoming data.
     *
     * @param {Object} mutation
     * @param {Object} variables
     * @param {Function} updateStore
     */
    mutate(mutation, variables, updateStore = (cached, incoming) => {}) {
      this.handleLoading(true);
      this.$apollo
        .mutate({
          mutation: mutation,
          variables: variables,
          update: (store, data) => {
            // TODO: Is data transformed properly?
            // Current implemented for create | patch
            // What does it return for delete?
            data = data.data[mutation.definitions[0].name.value].items;

            // Update cached data
            if (this.expandedQuery) {
              // Read the data from cache for query
              const cachedQuery = store.readQuery(this.expandedQuery);
              if (cachedQuery) {
                // Update the store
                const cachedQueryKey = Object.keys(cachedQuery)[0];
                cachedQuery[cachedQueryKey] = updateStore(
                  cachedQuery[cachedQueryKey],
                  data,
                );
                // Write data back to the cache
                store.writeQuery({ ...this.expandedQuery, data: cachedQuery });
              }
            }

            /**
             * Emits the store and data when graphQL updates
             * Use this to update the cached query if  affectedQuery or
             * updateStore was not provided
             *
             * @property {object} store
             * @property {object} updated object
             */
            this.$emit("update", store, data);
          },
        })
        .then((data) => {
          /**
           * Emits the data of a successful graphQL mutation
           *
           * @property {object} data
           */
          this.$emit("save", data);
        })
        .catch((error) => {
          this.handleError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
  },
};
