import { defineStore } from "pinia";

export const useAudioStore = defineStore("zsAudio", {
  state: () => ({
    /**
     * Minimum duration considered a dropout. Unit: milliseconds.
     * x > 0
     */
    minDurationInMs: 10,

    /**
     * Volume threshold considered zero. Unit: dB.
     * x < 0
     */
    threshold: -80.0,
  }),
  actions: {
    setMinDuration(newMinDuration: number) {
      this.minDurationInMs = Math.max(1, Math.round(newMinDuration));
    },
    setThreshold(newThreshold: number) {
      this.threshold = Math.min(0, newThreshold);
    },
  },
});
