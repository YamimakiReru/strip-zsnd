import TrimDropoutsService from "@/services/TrimDropoutsService";
import DetectZsndService, { DropoutInfo } from "@/services/DetectZsndService";
import LoadAudioService from "@/services/LoadAudioService";
import { ZsndWavChunk } from "@/services/wav_logic";
import { useAppStore } from "@/stores/ZsndAppStore";

import { useI18n } from "vue-i18n";
import { computed, ref } from "vue";
import { defineStore } from "pinia";

const MAX_UNDO_COUNT = 100;

class _UndoBufferEntry {
  constructor(
    /** Raw waveform samples used for editing. */
    public readonly rawAudioChunk: ZsndWavChunk<Float32Array>,
    public readonly audioBlobForPreview: Blob,
    public readonly dropouts: DropoutInfo[],
  ) {}
}

export const useAudioStore = defineStore("zsAudio", () => {
  const { t } = useI18n();
  const store = useAppStore();

  const minDurationInMs = ref(10);
  const threshold = ref(-80.0);
  const originalFilename = ref("");
  const originalSampleRate = ref(1);

  const undoBuffer = ref([] as _UndoBufferEntry[]);
  const undoBufferIndex = ref(0);

  function pushUndoBufferEntry(newEntry: _UndoBufferEntry) {
    // Removes all entries strictly after the current index.
    undoBuffer.value.splice(undoBufferIndex.value + 1);

    if (MAX_UNDO_COUNT <= undoBuffer.value.length) {
      undoBuffer.value.shift();
      --undoBufferIndex.value;
    }

    undoBuffer.value.push(newEntry);
    ++undoBufferIndex.value;
  }

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
    audioBlobForPreview: computed(() =>
      0 == undoBuffer.value.length
        ? null
        : undoBuffer.value[undoBufferIndex.value].audioBlobForPreview,
    ),

    /**
     * Detected dropout information.
     * Each entry contains the dropout start position and duration,
     * both expressed in samples.
     */
    dropouts: computed(() =>
      0 == undoBuffer.value.length
        ? null
        : undoBuffer.value[undoBufferIndex.value].dropouts,
    ),

    canUndo: computed(
      () => 0 < undoBuffer.value.length && 0 < undoBufferIndex.value,
    ),

    canRedo: computed(
      () => undoBufferIndex.value < undoBuffer.value.length - 1,
    ),

    setMinDuration(newMinDuration: number) {
      minDurationInMs.value = Math.max(1, Math.round(newMinDuration));
    },

    setThreshold(newThreshold: number) {
      threshold.value = Math.min(0, newThreshold);
    },

    undo() {
      if (0 >= undoBufferIndex.value) {
        throw new RangeError("No more undo steps!");
      }
      --undoBufferIndex.value;
    },

    redo() {
      if (undoBuffer.value.length <= undoBufferIndex.value + 1) {
        throw new RangeError("No more redo steps!");
      }
      ++undoBufferIndex.value;
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
        originalFilename.value = file.name;
        originalSampleRate.value = results.originalSampleRate;
        undoBufferIndex.value = 0;
        undoBuffer.value = [
          new _UndoBufferEntry(
            results.rawAudioChunk,
            results.audioBlobForPreview,
            results.dropouts,
          ),
        ];
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
      if (0 >= undoBuffer.value.length) {
        throw new Error("Attempt to rerun detection before loading a file!");
      }
      store.incrementBusyCounter();
      try {
        const service = new DetectZsndService();
        const currentEntry = undoBuffer.value[undoBufferIndex.value];

        const rawAudioChunk =
          currentEntry.rawAudioChunk as ZsndWavChunk<Float32Array>;
        const dropouts = await service.detect(
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

        const newEntry = new _UndoBufferEntry(
          rawAudioChunk,
          currentEntry.audioBlobForPreview,
          dropouts,
        );
        pushUndoBufferEntry(newEntry);
      } catch (exc) {
        console.error(exc);
        const msg = exc instanceof Error ? exc.message : String(exc);
        store.pushError(t("zsnd.error_during_dropout_detection", { exc: msg }));
      } finally {
        store.decrementBusyCounter();
        store.clearProgress();
      }
    },

    async trimDropoutAt(index: number) {
      store.incrementBusyCounter();
      try {
        const currentEntry = undoBuffer.value[undoBufferIndex.value];
        const { newChunk, newDropouts } = new TrimDropoutsService().trimAt(
          currentEntry.rawAudioChunk as ZsndWavChunk<Float32Array>,
          currentEntry.dropouts,
          index,
        );
        const newBlob = new LoadAudioService(t).loadFromChunk(
          newChunk,
          originalSampleRate.value,
        );
        const newEntry = new _UndoBufferEntry(newChunk, newBlob, newDropouts);
        pushUndoBufferEntry(newEntry);
      } finally {
        store.decrementBusyCounter();
      }
    },

    async trimAllDropouts() {
      store.incrementBusyCounter();
      try {
        const currentEntry = undoBuffer.value[undoBufferIndex.value];
        const newChunk = new TrimDropoutsService().trimAll(
          currentEntry.rawAudioChunk as ZsndWavChunk<Float32Array>,
          currentEntry.dropouts,
        );
        const newBlob = new LoadAudioService(t).loadFromChunk(
          newChunk,
          originalSampleRate.value,
        );
        const newEntry = new _UndoBufferEntry(newChunk, newBlob, []);
        pushUndoBufferEntry(newEntry);
      } finally {
        store.decrementBusyCounter();
      }
    },
  };
});
