import DetectZsndService, { DropoutInfo } from "@/services/DetectZsndService";
import LoadAudioService from "@/services/LoadAudioService";
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
  const originalFilename = ref("");
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

    originalFilename,

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

    setMinDuration(newMinDuration: number) {
      minDurationInMs.value = Math.max(1, Math.round(newMinDuration));
    },

    setThreshold(newThreshold: number) {
      threshold.value = Math.min(0, newThreshold);
    },

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
        originalFilename.value = file.name;
        originalSampleRate.value = results.originalSampleRate;
        dropouts.value = results.dropouts;

        audioBlobForPreview.value = results.audioBlobForPreview;
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

    async rerunDetection() {
      if (null == rawAudioChunk) {
        throw new Error("Attempt to rerun detection before loading a file!");
      }

      store.incrementBusyCounter();
      try {
        const service = new DetectZsndService();
        dropouts.value = await service.detect(
          {
            reportProgress: (position, total) => {
              store.setProgress((100 * position) / total);
            },
          },
          rawAudioChunk,
          originalSampleRate.value,
          minDurationInMs.value,
          threshold.value,
        );
      } catch (exc) {
        console.error(exc);
        const msg = exc instanceof Error ? exc.message : String(exc);
        store.pushError(t("zsnd.error_during_dropout_detection", { exc: msg }));
      } finally {
        store.decrementBusyCounter();
        store.clearProgress();
      }
    },
  };
});
