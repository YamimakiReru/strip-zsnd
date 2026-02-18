<script setup lang="ts">
import { useAudioStore } from "@/stores/AudioStore";
import { usePortraitFlagUpdater } from "@/stores/ZsndAppStore";
import WaveformControls from "@/features/WaveformControls.vue";
import InputBoxWithPreset from "@/components/InputBoxWithPreset.vue";
import ThemeChooser from "@/components/ThemeChooser.vue";
import LanguageChooser from "@/components/LanguageChooser.vue";
import ErrorBox from "@/components/ErrorBox.vue";
import LoadingIndicator from "@/components/LoadingIndicator.vue";

import {
  MoonIcon as MoonIcon16,
  ClockIcon,
  SpeakerXMarkIcon,
} from "@heroicons/vue/16/solid";
import {
  MoonIcon as MoonIcon24,
  ArrowPathIcon,
  ArrowDownIcon,
} from "@heroicons/vue/24/solid";
import { useI18n } from "vue-i18n";
import { computed, ref } from "vue";

const { t } = useI18n();
usePortraitFlagUpdater();
const audioStore = useAudioStore();
const minDuration = computed({
  get: () => audioStore.minDurationInMs,
  set: (v: number) => audioStore.setMinDuration(v),
});
const threshold = computed({
  get: () => audioStore.threshold,
  set: (v: number) => audioStore.setThreshold(v),
});

const _confirmRerunDetectionDialog = ref<HTMLDialogElement | null>(null);

const _downloadFilename = computed(() => {
  if (!audioStore.originalFilename) {
    return "audio.wav";
  } else {
    const dotPos = audioStore.originalFilename.lastIndexOf(".");
    return -1 == dotPos
      ? `${audioStore.originalFilename}-fix.wav`
      : `${audioStore.originalFilename.substring(0, dotPos)}-fix.wav`;
  }
});

const _downloadUrl = computed(() => {
  if (audioStore.audioBlobForPreview) {
    return URL.createObjectURL(audioStore.audioBlobForPreview);
  } else {
    return "";
  }
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

function _doRerunDetection() {
  audioStore.rerunDetection();
  _confirmRerunDetectionDialog.value?.close();
}
</script>

<template>
  <div class="relative w-full h-full portrait:md:p-4 lg:p-4">
    <LoadingIndicator />
    <div class="w-full h-full flex flex-col gap-2 p-2 bg-base-300 rounded-lg">
      <div class="flex flex-col landscape:flex-row md:flex-row gap-2">
        <div class="flex">
          <div class="dropdown">
            <div tabindex="0" role="button" class="btn btn-sm md:btn-md btn-neutral text-neutral-content">
              <MoonIcon16 class="w-4 h-4 md:hidden" />
              <MoonIcon24 class="w-6 h-6 hidden md:block" />
            </div>
            <ul
              tabindex="-1"
              class="dropdown-content menu flex-nowrap overflow-y-scroll max-h-[80vh] bg-base-100 rounded-box z-10 p-2 shadow-2xl"
            >
              <LanguageChooser />
              <ThemeChooser default-theme="synthwave" />
            </ul>
          </div>
          <div class="join">
            <input
              type="file"
              @change="_onFileChange"
              accept=".wav"
              class="file-input file-input-sm md:file-input-md text-base-content/50 join-item"
            />
            <button
              type="button"
              @click="_confirmRerunDetectionDialog?.showModal()"
              :disabled="null == audioStore.audioBlobForPreview"
              class="btn btn-sm md:btn-md join-item"
            >
              <ArrowPathIcon class="w-6 h-6" />
            </button>
            <a
              :download="_downloadFilename"
              :href="_downloadUrl"
              class="btn btn-sm md:btn-md join-item"
              :class="{
                'btn-disabled': null == audioStore.audioBlobForPreview,
              }"
            >
              <ArrowDownIcon class="w-6 h-6" />
            </a>
          </div>
        </div>
        <div class="flex gap-2">
          <InputBoxWithPreset
            :label="t('zsnd.min_duration')"
            unit="ms"
            v-model="minDuration"
            :presets="[5, 10, 30, 50, 100]"
            :input-attrs="{ step: 1, min: 1, required: true }"
            input-container-class="input-sm md:input-md"
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
            input-container-class="input-sm md:input-md"
          >
            <template #icon>
              <SpeakerXMarkIcon class="h-4 w-4" />
            </template>
          </InputBoxWithPreset>
        </div>
      </div>
      <ErrorBox />
      <WaveformControls class="grow" />
    </div>
    <dialog ref="_confirmRerunDetectionDialog" class="modal">
      <div class="modal-box">
        <p class="py-4">{{ t("zsnd.confirm_rerun_detection") }}</p>
        <div class="modal-action">
          <form method="dialog">
            <button
              type="button"
              @click="_doRerunDetection"
              class="btn btn-primary"
            >
              {{ t("app.yes") }}
            </button>
            <button class="btn">{{ t("app.no") }}</button>
          </form>
        </div>
      </div>
    </dialog>
  </div>
</template>
