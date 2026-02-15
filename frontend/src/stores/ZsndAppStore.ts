import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useAppStore = defineStore("zsApp", () => {
  const errors = ref([] as string[]);
  const busyCounter = ref(0);
  const progress = ref(null as number | null);

  return {
    errors,
    busyCounter,
    progress,

    isBusy: computed(() => busyCounter.value > 0),

    pushError(msg: string) {
      errors.value.push(msg);
    },

    removeErrorAt(index: number) {
      errors.value.splice(index, 1);
    },

    incrementBusyCounter() {
      ++busyCounter.value;
    },

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
  };
});
