import { defineStore } from "pinia";

export const useAppStore = defineStore("zsApp", {
  state: () => ({
    errors: [] as string[],
    busyCounter: 0,
    progress: null as number | null,
  }),
  actions: {
    pushError(msg: string) {
      this.errors.push(msg);
    },
    removeErrorAt(index: number) {
      this.errors.splice(index, 1);
    },
    incrementBusyCounter() {
      this.busyCounter++;
    },
    decrementBusyCounter() {
      this.busyCounter = Math.max(0, this.busyCounter - 1);
    },
    /**
     * @param {number} newProgress
     *   Raw progress value. This function clamps it to the range 0–100
     *   and rounds it to the nearest integer.
     */
    setProgress(newProgress: number) {
      this.progress = Math.round(Math.min(100, Math.max(0, newProgress)));
    },
    clearProgress() {
      this.progress = null;
    },
  },
  getters: {
    isBusy: (state) => state.busyCounter > 0,
  },
});
