import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useAppStore = defineStore("zsApp", () => {
  const errors = ref([] as string[]);
  const busyCounter = ref(0);
  const progress = ref(null as number | null);
  const isPortrait = ref(false);

  return {
    /** Error messages. */
    errors,

    /**
     * Number of active jobs.
     * When the value is greater than 0, a full‑screen spinner is shown and user input is blocked.
     */
    busyCounter,

    /**
     * Progress percentage displayed to the user when the system is busy.
     * Valid range: 0 to 100.
     */
    progress,

    /** Page orientation flag. "Portrait" usually corresponds to height > width, but not always. */
    isPortrait,

    isBusy: computed(() => busyCounter.value > 0),

    /** Displays a human‑readable error message to the user. */
    pushError(msg: string) {
      errors.value.push(msg);
    },

    /** Removes a human‑readable error message at the given index. */
    removeErrorAt(index: number) {
      errors.value.splice(index, 1);
    },

    /** Increments the busy counter, causing the UI to enter a busy state. */
    incrementBusyCounter() {
      ++busyCounter.value;
    },

    /** Decrements the busy counter. When the counter reaches 0, the UI becomes interactive again. */
    decrementBusyCounter() {
      busyCounter.value = Math.max(0, busyCounter.value - 1);
    },

    /**
     * @param {number} newProgress
     *   Raw progress value. This function clamps it to the range 0–100
     *   and rounds it to the nearest integer.
     */
    setProgress(newProgress: number) {
      progress.value = Math.round(Math.min(100, Math.max(0, newProgress)));
    },

    clearProgress() {
      progress.value = null;
    },

    /** @see ZsndApp */
    updateIsPortrait(newState: boolean) {
      isPortrait.value = newState;
    },
  };
});
