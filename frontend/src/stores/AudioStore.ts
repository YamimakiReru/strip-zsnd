import DetectZsndService from "@/services/DetectZsndService";
import { ZsndWavChunk } from "@/services/wav_logic";
import { useAppStore } from "@/stores/ZsndAppStore";

import WavDecoder from "wav-decoder";
import WavEncoder from "wav-encoder";
import { useI18n } from "vue-i18n";
import { ref } from "vue";
import { defineStore } from "pinia";

export const useAudioStore = defineStore("zsAudio", () => {
  const { t } = useI18n();
  const store = useAppStore();

  const minDurationInMs = ref(10);
  const threshold = ref(-80.0);
  const audioBlobForPreview = ref(null as Blob | null);

  async function _callDetectService(audioData: WavDecoder.AudioData) {
    const chunk = new ZsndWavChunk(audioData.channelData[0]);
    const dropouts = await new DetectZsndService().detect(
      {
        reportProgress: (position, total) => {
          store.setProgress((100 * position) / total);
        },
      },
      chunk,
      audioData.sampleRate,
      minDurationInMs.value,
      threshold.value,
    );
    const reArrBuf = WavEncoder.encode.sync(audioData, {
      float: true,
      bitDepth: 32,
    });
    audioBlobForPreview.value = new Blob([reArrBuf]);
  }

  return {
    audioBlobForPreview,

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

    setMinDuration(newMinDuration: number) {
      minDurationInMs.value = Math.max(1, Math.round(newMinDuration));
    },

    setThreshold(newThreshold: number) {
      threshold.value = Math.min(0, newThreshold);
    },

    async loadFile(file: File) {
      store.incrementBusyCounter();
      try {
        const arrBuf = await file.arrayBuffer();
        const audioData = WavDecoder.decode.sync(arrBuf);
        if (1 !== audioData.channelData.length) {
          store.pushError(t("zsnd.mono_only_supported"));
          return;
        }
        await _callDetectService(audioData);
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
  };
});
