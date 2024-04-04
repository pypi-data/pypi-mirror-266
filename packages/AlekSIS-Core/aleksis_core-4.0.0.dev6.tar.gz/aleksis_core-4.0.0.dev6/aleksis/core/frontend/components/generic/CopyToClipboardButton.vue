<template>
  <v-tooltip bottom :open-on-hover="hover" v-model="tooltipModel">
    <template #activator="{ on, attrs }">
      <v-layout wrap v-on="on" v-bind="attrs">
        <v-btn fab x-small icon @click.stop="copyToClipboard(text)">
          <v-scroll-x-transition mode="out-in">
            <v-icon :key="clipboardIcon">
              {{ clipboardIcon }}
            </v-icon>
          </v-scroll-x-transition>
        </v-btn>
      </v-layout>
    </template>
    <span>{{ tooltipText }}</span>
  </v-tooltip>
</template>

<script>
export default {
  name: "CopyToClipboardButton",
  data() {
    return {
      copied: false,
      tooltipModel: false,
      hover: true,
    };
  },
  props: {
    text: {
      type: String,
      required: true,
    },
    tooltipHelpText: {
      type: String,
      default: "",
    },
  },
  computed: {
    tooltipText() {
      return this.copied
        ? this.$t("actions.copied")
        : this.tooltipHelpText
          ? this.tooltipHelpText
          : this.$t("actions.copy");
    },
    clipboardIcon() {
      return this.copied
        ? "mdi-clipboard-check-outline"
        : "mdi-clipboard-outline";
    },
  },
  methods: {
    copyToClipboard(text) {
      navigator.clipboard.writeText(text);
      this.tooltipModel = false;
      setTimeout(() => {
        this.tooltipModel = this.copied = true;
        this.hover = false;
        setTimeout(() => {
          this.tooltipModel = this.copied = false;
          this.hover = true;
        }, 1000);
      }, 100);
    },
  },
};
</script>
