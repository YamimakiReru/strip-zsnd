<script setup lang="ts">
import DropoutView from "@/features/DropoutView.vue";
import { useAudioStore } from "@/stores/AudioStore";
import { useAppStore } from "@/stores/ZsndAppStore";
import { formatAudioPosition } from "@/util";
import WaveSurferZoomBar from "@/components/WaveSurferZoomBar.vue";
import MovableDivider from "@/components/MovableDivider.vue";

import WaveSurfer from "wavesurfer.js";
import {
  useWaveSurfer,
  useWaveSurferTimeline,
  useWaveSurferMinimap,
  useWaveSurferHover,
  useWaveSurferRegions,
} from "@meersagor/wavesurfer-vue";
import { InformationCircleIcon } from "@heroicons/vue/24/solid";
import { useI18n } from "vue-i18n";
import { onMounted, onBeforeUnmount, watch, nextTick, Ref, ref } from "vue";

const { t } = useI18n();
const store = useAppStore();
const audioStore = useAudioStore();

let _positionAtPlayStart = 0;

const _waveSurferDivRef = ref<HTMLElement | null>(null);
const _ws = useWaveSurfer({
  containerRef: _waveSurferDivRef,
  options: { normalize: true, autoCenter: true },
});

const _rawWaveSurfer = _ws.waveSurfer as any as Ref<WaveSurfer | null>;
useWaveSurferTimeline({
  waveSurfer: _rawWaveSurfer,
  timelineOptions: {
    height: 32,
    timeInterval: 0.1,
    secondaryLabelInterval: 1.0,
  },
});
useWaveSurferMinimap({
  waveSurfer: _rawWaveSurfer,
  minimapOptions: { height: 64 },
});
useWaveSurferHover({
  waveSurfer: _rawWaveSurfer,
  hoverOptions: {
    labelSize: "1.5rem",
    formatTimeCallback: formatAudioPosition,
  },
});
const { regionsPlugin: _regionsPlugin } = useWaveSurferRegions({
  waveSurfer: _rawWaveSurfer,
});

// Load the audio into wavesurfer.js after reading the file as a Blob.
watch(
  () => audioStore.audioBlobForPreview,
  async (blob: Blob | null) => {
    if (null == blob) {
      store.errors.push("Unload operation is not yet implemented.");
      return;
    }

    store.incrementBusyCounter();
    try {
      if (!_ws.waveSurfer.value) {
        throw new Error("waveSurfer must not be null.");
      }
      // Generating the preview at the original sample rate is too costly.
      // _ws.waveSurfer.value.setOptions({sampleRate: audioStore.originalSampleRate})
      await _ws.waveSurfer.value.loadBlob(blob);
      // _ws.waveSurfer.value.seekTo(0);
    } finally {
      store.decrementBusyCounter();
    }
  },
);

onMounted(async () => {
  await nextTick();

  window.addEventListener("keyup", _playPauseOnKeyUp);

  // Ensure that WaveSurfer fills the remaining space.
  const shadowRoot =
    _waveSurferDivRef.value?.querySelector(":scope >div")?.shadowRoot;
  if (!shadowRoot) {
    throw new Error("Assume that WaveSurfer has a shadowRoot.");
  }
  const styleElement = shadowRoot.querySelector("style");
  if (!styleElement) {
    throw new Error("Assume that WaveSurfer has a <style> element.");
  }
  styleElement.textContent += `
:where(.canvases, .progress) >div,
:where(.canvases, .progress) canvas {height: 100% !important}`;
});
onBeforeUnmount(() => {
  window.removeEventListener("keyup", _playPauseOnKeyUp);
});

function _playPause() {
  if (_ws.isPlaying.value) {
    _ws.waveSurfer.value?.pause();
    _ws.waveSurfer.value?.setTime(_positionAtPlayStart);
  } else {
    _positionAtPlayStart = _ws.waveSurfer.value?.getCurrentTime() ?? 0;
    _ws.waveSurfer.value?.play();
  }
}

function _playPauseOnKeyUp(event: KeyboardEvent) {
  if (event.defaultPrevented) {
    // the event was already processed by another component.
    return;
  }
  if (![" ", "Enter"].includes(event.key)) {
    return;
  }
  if (
    event.target instanceof HTMLInputElement ||
    event.target instanceof HTMLButtonElement ||
    event.target instanceof HTMLSelectElement
  ) {
    return;
  }
  _playPause();
}
</script>

<template>
  <!-- Without a defined min-height or min-width, a flex child with flex-grow may overflow its parent. -->
  <div :class="$attrs.class" class="min-h-0 flex flex-col gap-2">
    <div
      v-if="_ws.isReady.value"
      class="flex flex-col md:flex-row landscape:flex-row gap-2"
    >
      <div class="flex items-center gap-2">
        <button @click="_playPause()" class="w-24 btn btn-primary">
          {{ _ws.isPlaying.value ? t("app.pause") : t("app.play") }}
        </button>
        <div class="join">
          <button
            type="button"
            @click="_ws.waveSurfer.value?.skip(-1)"
            class="btn join-item"
          >
            -1s
          </button>
          <button
            type="button"
            @click="_ws.waveSurfer.value?.skip(+1)"
            class="btn join-item"
          >
            +1s
          </button>
        </div>
        {{ formatAudioPosition(_ws.currentTime.value) }} /
        {{ formatAudioPosition(_ws.totalDuration.value) }}
      </div>
      <WaveSurferZoomBar
        :wave-surfer="_rawWaveSurfer"
        :container="_waveSurferDivRef"
        class="grow"
      />
    </div>
    <div
      v-if="_ws.isReady.value"
      role="alert"
      class="hidden lg:grid alert alert-info text-info-content"
    >
      <InformationCircleIcon class="w-6 h-6" />
      {{ t("zsnd.tips.keyboard_shortcut_play_pause") }}
    </div>
    <div class="min-h-0 flex portrait:flex-col grow">
      <div
        ref="_waveSurferDivRef"
        id="zs-waveform-controls"
        class="overflow-hidden w-(--zs-waveform-ctl-width,60%) portrait:w-full portrait:h-(--zs-waveform-ctl-height,60%)"
      ></div>
      <MovableDivider
        :resize-target="_waveSurferDivRef"
        :css-property-name="
          store.isPortrait
            ? '--zs-waveform-ctl-height'
            : '--zs-waveform-ctl-width'
        "
        :orientation="store.isPortrait ? 'vertical' : 'horizontal'"
        :min="30"
        :max="90"
      />
      <DropoutView
        :wave-surfer="_rawWaveSurfer"
        :regions-plugin="_regionsPlugin"
        class="grow portrait:h-0 portrait:w-full"
      />
    </div>
  </div>
</template>
