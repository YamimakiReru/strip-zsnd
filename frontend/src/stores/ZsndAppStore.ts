import { defineStore } from "pinia"

export const useAppStore = defineStore('zsApp', {
  state: () => ({
    busyCounter: 0,
    progess: null as number | null,
  }),
  actions: {
    incrementBusyCounter() {
      this.busyCounter++
    },
    decrementBusyCounter() {
      this.busyCounter = Math.max(0, this.busyCounter - 1)
    },
    /**
     * @param {number} newProgress
     *   Raw progress value. This function clamps it to the range 0–100
     *   and rounds it to the nearest integer.
     */
    setProgress(newProgress: number) {
      this.progess = Math.round(Math.min(100, Math.max(0, newProgress)))
    },
    clearProgress() {
      this.progess = null
    }
  },
  getters: {
    isBusy: (state) => state.busyCounter > 0,
    progress: (state) => state.progess,
  },
})
