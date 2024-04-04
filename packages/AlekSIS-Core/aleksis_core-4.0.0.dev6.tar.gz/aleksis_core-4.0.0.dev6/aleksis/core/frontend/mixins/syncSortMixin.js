/**
 * Sync v-data-table and v-data-iterator ordering to backend ordering
 * (via gqlOrderBy of queryMixin)
 */
export default {
  data() {
    return {
      sortBy: [],
      sortDesc: [],
      orderBy: [],
    };
  },
  methods: {
    snakeCase(string) {
      return string
        .replace(/\W+/g, " ")
        .split(/ |\B(?=[A-Z])/)
        .map((word) => word.toLowerCase())
        .join("_");
    },
    orderKey(value, desc) {
      const key =
        this.$attrs.headers.find((header) => header.value === value).orderKey ||
        this.snakeCase(value);
      return (desc ? "-" : "") + key;
    },
    handleSortChange() {
      this.orderBy = this.sortBy.map((value, key) =>
        this.orderKey(value, this.sortDesc[key]),
      );
    },
  },
};
