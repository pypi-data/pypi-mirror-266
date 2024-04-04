<template>
  <router-link
    v-bind="$attrs"
    v-on="$listeners"
    class="text-decoration-none primary--text font-weight-medium d-inline-block full-width"
  >
    <slot />
  </router-link>
</template>
<script>
export default {
  name: "TableLink",
  extends: "router-link",
};
</script>
