/**
 * Vue mixin containing permission checking code.
 */

const permissionsMixin = {
  methods: {
    checkPermission(permissionName) {
      return (
        this.$root.permissions &&
        this.$root.permissions.find((p) => p.name === permissionName) &&
        this.$root.permissions.find((p) => p.name === permissionName).result
      );
    },
    addPermissions(newPermissionNames) {
      const keepPermissionNames = this.$root.permissionNames.filter(
        (oldPermName) =>
          !newPermissionNames.find(
            (newPermName) => newPermName === oldPermName,
          ),
      );

      this.$root.permissionNames = [
        ...keepPermissionNames,
        ...newPermissionNames,
      ];
    },
  },
};

export default permissionsMixin;
