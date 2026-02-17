import LoadAudioService from "@/services/LoadAudioService";
import { DropoutInfo } from "@/services/DetectZsndService";
import { ZsndWavChunk } from "@/services/wav_logic";
import { useAppStore } from "@/stores/ZsndAppStore";

import { useI18n } from "vue-i18n";
import { ref } from "vue";
import { defineStore } from "pinia";

export const useAudioStore = defineStore("zsAudio", () => {
  const { t } = useI18n();
  const store = useAppStore();

  const minDurationInMs = ref(10);
  const threshold = ref(-80.0);
  const originalSampleRate = ref(1);
  const audioBlobForPreview = ref(null as Blob | null);
  const dropouts = ref([] as DropoutInfo[]);

  /** Raw waveform samples used for editing. */
  let rawAudioChunk = null as ZsndWavChunk<Float32Array> | null;

  return {
    /**
     * Minimum duration considered a dropout. Unit: milliseconds.
     * x > 0
     */
    minDurationInMs,

    /**
     * Volume threshold considered zero. Unit: dB.
     * x < 0
     */
    threshold,

    /** The sample rate (Hz) of the original audio source. */
    originalSampleRate,

    /** Blob objects are immutable, so storing them in a ref is safe. */
    audioBlobForPreview,

    /**
     * Detected dropout information.
     * Each entry contains the dropout start position and duration,
     * both expressed in samples.
     */
    dropouts,

    async loadFile(file: File) {
      store.incrementBusyCounter();
      try {
        const service = new LoadAudioService(t);
        const results = await service.loadFile(
          file,
          minDurationInMs.value,
          threshold.value,
          {
            reportProgress: (position, total) => {
              store.setProgress((100 * position) / total);
            },
          },
        );

        rawAudioChunk = results.rawAudioChunk;
        originalSampleRate.value = results.originalSampleRate;
        audioBlobForPreview.value = results.audioBlobForPreview;
        dropouts.value = results.dropouts;
      } catch (exc) {
        console.error(exc);
        const msg = exc instanceof Error ? exc.message : String(exc);
        store.pushError(
          t("app.input_file_cannot_be_opened", {
            filename: file.name,
            exc: msg,
          }),
        );
      } finally {
        store.decrementBusyCounter();
        store.clearProgress();
      }
    },

    setMinDuration(newMinDuration: number) {
      minDurationInMs.value = Math.max(1, Math.round(newMinDuration));
    },

    setThreshold(newThreshold: number) {
      threshold.value = Math.min(0, newThreshold);
    },
  };
});
