<script setup lang="ts">
import DetectZsndService from "@/services/DetectZsndService";
import { ZsndWavChunk } from "@/services/wav_logic";
import { useAudioStore } from "@/stores/AudioStore";
import { useAppStore } from "@/stores/ZsndAppStore";
import WaveformControls from "@/features/WaveformControls.vue";
import ThemeChooser from "@/components/ThemeChooser.vue";
import LanguageChooser from "@/components/LanguageChooser.vue";
import ErrorBox from "@/components/ErrorBox.vue";

import WavEncoder from "wav-encoder";
import WavDecoder from "wav-decoder";
import { useI18n } from "vue-i18n";
import { ref } from "vue";

const { t } = useI18n();
const store = useAppStore();
const audioStore = useAudioStore();
const _waveformControls = ref<InstanceType<typeof WaveformControls> | null>(
  null,
);

async function _onFileChange(event: Event) {
  const inputElement = event.target as HTMLInputElement;
  const selectedFile = inputElement.files?.[0];
  if (!selectedFile) {
    return;
  }

  store.incrementBusyCounter();
  try {
    const arrBuf = await selectedFile.arrayBuffer();
    const audioData = WavDecoder.decode.sync(arrBuf);
    if (1 !== audioData.channelData.length) {
      store.pushError(t("zsnd.mono_only_supported"));
      return;
    }

    await _callDetectService(audioData);

    // Blur the focus to prevent the file from reloading
    // when the user presses Enter repeatedly.
    if (event.target instanceof HTMLElement) {
      event.target.blur();
    }
  } catch (exc) {
    console.error(exc);
    const msg = exc instanceof Error ? exc.message : String(exc);
    store.pushError(
      t("app.input_file_cannot_be_opened", {
        filename: selectedFile.name,
        exc: msg,
      }),
    );
  } finally {
    store.decrementBusyCounter();
    store.clearProgress();
  }
}

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
    audioStore.minDurationInMs,
    audioStore.threshold,
  );

  const reArrBuf = WavEncoder.encode.sync(audioData, {
    float: true,
    bitDepth: 32,
  });
  const blob = new Blob([reArrBuf]);
  await _waveformControls.value?.loadBlob(blob);
}
</script>

<template>
  <div class="fixed inset-0 portrait:md:p-4 lg:p-4">
    <!-- loading spinner -->
    <div
      v-if="store.isBusy"
      class="z-50 fixed inset-0 bg-neutral/50 flex items-center justify-center"
    >
      <div
        v-if="null != store.progress"
        class="radial-progress text-primary text-5xl"
        role="progressbar"
        :style="{
          '--value': store.progress,
          '--size': '80vmin',
          '--thickness': '2rem',
        }"
        :aria-valuenow="store.progress"
      >
        {{ store.progress }}%
      </div>
      <div
        v-else
        class="loading loading-spinner loading-xl -scale-800 text-primary"
      ></div>
    </div>
    <!-- body -->
    <div
      class="w-full h-full flex flex-col gap-2 max-w-5xl mx-auto p-2 bg-neutral text-neutral-content rounded-lg"
    >
      <div class="flex gap-2">
        <div class="flex flex-col landscape:flex-row md:flex-row gap-1">
          <input
            type="file"
            @change="_onFileChange"
            accept=".wav"
            class="file-input file-input-sm md:file-input-md text-base-content/50"
          />
          <div class="flex gap-2">
            <div class="dropdown">
              <label class="input input-sm md:input-md text-base-content">
                <span class="label gap-0"
                  >MinDur<span class="hidden md:inline">ation</span></span
                >
                <input
                  type="number"
                  :value="audioStore.minDurationInMs"
                  @change="
                    (ev: any) => audioStore.setMinDuration(ev.target.value)
                  "
                  step="1"
                  min="1"
                  required
                />
                <span class="label"><span class="hidden md:inline landscape:inline">ms</span></span>
              </label>
              <ul
                tabindex="0"
                class="dropdown-content menu p-2 shadow bg-base-100 text-base-content rounded-box w-full mt-1"
              >
                <li v-for="n of [5, 10, 30, 50, 100]" :key="`dur${n}`">
                  <a @click="audioStore.setMinDuration(n)">{{ n }} ms</a>
                </li>
              </ul>
            </div>
            <div class="dropdown dropdown-end">
              <label class="input input-sm md:input-md text-base-content">
                <span class="label gap-0"
                  >T<span class="hidden md:inline landscape:inline">hreshold</span></span
                >
                <input
                  type="number"
                  :value="audioStore.threshold"
                  @change="
                    (ev: any) => audioStore.setThreshold(ev.target.value)
                  "
                  max="0"
                  required
                />
                <span class="label"><span class="hidden md:inline landscape:inline">dB</span></span>
              </label>
              <ul
                tabindex="0"
                class="dropdown-content menu p-2 shadow bg-base-100 text-base-content rounded-box w-full mt-1"
              >
                <li v-for="n of [-80, -75, -70, -65, -60]" :key="`th${n}`">
                  <a @click="audioStore.setThreshold(n)">{{ n }} dB</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="flex flex-col landscape:flex-row md:flex-row gap-1">
          <ThemeChooser />
          <LanguageChooser />
        </div>
      </div>
      <ErrorBox />
      <WaveformControls ref="_waveformControls" class="grow" />
    </div>
  </div>
</template>
