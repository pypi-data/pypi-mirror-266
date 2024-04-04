/**
 * Mixin with utilities for AlekSIS view components.
 */
import { DateTime } from "luxon";

const aleksisMixin = {
  data: () => {
    return {
      $_aleksis_safeTrackedEvents: new Array(),
    };
  },
  methods: {
    safeAddEventListener(target, event, handler) {
      console.debug("Safely adding handler for %s on %o", event, target);
      target.addEventListener(event, handler);
      // Add to tracker so we can unregister the handler later
      this.$data.$_aleksis_safeTrackedEvents.push({
        target: target,
        event: event,
        handler: handler,
      });
    },
    $toast(messageKey, state, timeout) {
      this.$root.snackbarItems.push({
        id: crypto.randomUUID(),
        timeout: timeout || 5000,
        messageKey: this.$t(messageKey),
        color: state || "error",
      });
    },
    $toastError(messageKey, timeout) {
      this.$toast(messageKey || "generic_messages.error", "error", timeout);
    },
    $toastSuccess(messageKey, timeout) {
      this.$toast(messageKey || "generic_messages.success", "success", timeout);
    },
    $toastInfo(messageKey, timeout) {
      this.$toast(messageKey, "info", timeout);
    },
    $toastWarning(messageKey, timeout) {
      this.$toast(messageKey, "warning", timeout);
    },
    $parseISODate(value) {
      return DateTime.fromISO(value);
    },
    /**
     * Generic error handler
     * Logs to console, emits an error event &
     * posts a suitable message to the snackbar
     */
    handleError(error, errorCode) {
      // TODO: Do more with errorCode
      //       & document it more
      console.error(error, "ErrorCode:", errorCode);
      /**
       * Emits an error
       */
      this.$emit("error", error);
      if (error instanceof String) {
        // error is a translation key or simply a string
        this.$toastError(error);
      } else if (
        error instanceof Object &&
        error.message &&
        error.message instanceof String
      ) {
        // error object has a message string
        this.$toastError(error.message);
      } else {
        // FIXME: This catch all is specialized on graphql errors
        //        For now this behaviour is reproduced since it was
        //        already used in the handleError methods preceding
        //        this centralization.
        this.$toastError("graphql.snackbar_error_message");
      }
    },
  },
  mounted() {
    this.$emit("mounted");
  },
  beforeDestroy() {
    // Unregister all safely added event listeners as to not leak them
    for (let trackedEvent in this.$data.$_aleksis_safeTrackedEvents) {
      if (trackedEvent.target) {
        console.debug(
          "Removing handler for %s on %o",
          trackedEvent.event,
          trackedEvent.target,
        );
        trackedEvent.target.removeEventListener(
          trackedEvent.event,
          trackedEvent.handler,
        );
      } else {
        console.debug("Target already removed while removing event handler");
      }
    }
  },
};

export default aleksisMixin;
