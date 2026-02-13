import { defineStore } from "pinia"

export const useAppStore = defineStore('zsApp', {
  state: () => ({
    busyCounter: 0,
  }),
  actions: {
    incrementBusyCounter() {
      this.busyCounter++
    },
    decrementBusyCounter() {
      this.busyCounter = Math.max(0, this.busyCounter - 1)
    },
  },
  getters: {
    isBusy: (state) => state.busyCounter > 0,
  },
})
