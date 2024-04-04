import loadingMixin from "./loadingMixin.js";

/**
 * This mixin provides generic item query via graphQL.
 * The query result is available in items.
 */
export default {
  mixins: [loadingMixin],
  props: {
    /**
     * The graphQL query
     */
    gqlQuery: {
      type: Object,
      required: true,
    },
    /**
     * Optional arguments to graphQL query
     */
    // UPDATE NOTICE: Name change from additionalQueryArgs (prop was so far not used anyway)
    gqlAdditionalQueryArgs: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * OrderBy directive used in the graphQL query
     */
    gqlOrderBy: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Filter object used in the graphQL query
     */
    gqlFilters: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * Transform function for the data returned by the query
     */
    getGqlData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
  },
  emits: ["items", "lastQuery"],
  data() {
    return {
      internalAdditionalFilters: {},
      filterString: "{}",
      lastQuery: {},
    };
  },
  computed: {
    additionalFilters: {
      get() {
        return this.internalAdditionalFilters;
      },
      set(filters) {
        this.internalAdditionalFilters = filters;
        this.updateFilterString();
      },
    },
  },
  watch: {
    gqlFilters: {
      handler() {
        this.updateFilterString();
      },
      deep: true,
    },
  },
  methods: {
    handleItems(items) {
      return items;
    },
    updateFilterString() {
      this.filterString = JSON.stringify({
        ...this.gqlFilters,
        ...this.internalAdditionalFilters,
      });
    },
  },
  apollo: {
    items() {
      return {
        query: this.gqlQuery,
        variables() {
          const orderBy = this.gqlOrderBy.length
            ? { orderBy: this.gqlOrderBy }
            : {};
          const filters = {
            filters: this.filterString,
          };
          return {
            ...this.gqlAdditionalQueryArgs,
            ...orderBy,
            ...filters,
          };
        },
        watchLoading(loading) {
          this.handleLoading(loading);
        },
        error: (error) => {
          this.handleError(error);
        },
        update: (data) => {
          this.lastQuery = this.$apollo.queries.items;
          /**
           * Emits the last query
           * Use this to update the cache
           *
           * @property {Object} graphQL query
           */
          this.$emit("lastQuery", this.lastQuery);
          const items = this.handleItems(this.getGqlData(data.items));
          /**
           * Emits updated items
           * either from a graphQL query
           * or if the cached result was updated.
           *
           * @property {array} Query restult
           */
          this.$emit("items", items);
          return items;
        },
      };
    },
  },
};
