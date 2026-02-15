<script setup lang="ts">
import { useAudioStore } from "@/stores/AudioStore";
import WaveformControls from "@/features/WaveformControls.vue";
import InputBoxWithPreset from "@/components/InputBoxWithPreset.vue";
import ThemeChooser from "@/components/ThemeChooser.vue";
import LanguageChooser from "@/components/LanguageChooser.vue";
import ErrorBox from "@/components/ErrorBox.vue";
import LoadingIndicator from "@/components/LoadingIndicator.vue";

import { ClockIcon, SpeakerXMarkIcon } from "@heroicons/vue/16/solid";
import { useI18n } from "vue-i18n";
import { computed } from "vue";

const { t } = useI18n();
const audioStore = useAudioStore();
const minDuration = computed({
  get: () => audioStore.minDurationInMs,
  set: (v: number) => audioStore.setMinDuration(v),
});
const threshold = computed({
  get: () => audioStore.threshold,
  set: (v: number) => audioStore.setThreshold(v),
});

async function _onFileChange(event: Event) {
  const inputElement = event.target as HTMLInputElement;
  const selectedFile = inputElement.files?.[0];
  if (!selectedFile) {
    return;
  }
  await audioStore.loadFile(selectedFile);

  // Blur the focus to prevent the file from reloading
  // when the user presses Enter repeatedly.
  if (event.target instanceof HTMLElement) {
    event.target.blur();
  }
}
</script>

<template>
  <div class="relative w-full h-full portrait:md:p-4 lg:p-4">
    <LoadingIndicator />
    <div
      class="w-full h-full flex flex-col gap-2 p-2 bg-neutral text-neutral-content rounded-lg"
    >
      <div class="flex gap-2">
        <div class="grow flex flex-col landscape:flex-row md:flex-row gap-1">
          <input
            type="file"
            @change="_onFileChange"
            accept=".wav"
            class="file-input file-input-sm md:file-input-md text-base-content/50"
          />
          <div class="flex gap-2">
            <InputBoxWithPreset
              :label="t('zsnd.min_duration')"
              unit="ms"
              v-model="minDuration"
              :presets="[5, 10, 30, 50, 100]"
              :input-attrs="{ step: 1, min: 1, required: true }"
            >
              <template #icon>
                <ClockIcon class="h-4 w-4" />
              </template>
            </InputBoxWithPreset>
            <InputBoxWithPreset
              :label="t('zsnd.threshold')"
              unit="dB"
              v-model="threshold"
              :presets="[-80, -75, -70, -65, -60]"
              :input-attrs="{ max: 0, required: true }"
            >
              <template #icon>
                <SpeakerXMarkIcon class="h-4 w-4" />
              </template>
            </InputBoxWithPreset>
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
