<script setup lang="ts">
import { useAppStore } from "@/stores/ZsndAppStore"
import { formatAudioPosition } from "@/util"

import {
  useWaveSurfer,
  useWaveSurferTimeline,
  useWaveSurferMinimap,
  useWaveSurferHover
} from "@meersagor/wavesurfer-vue"
import WaveSurferZoomPlugin from "wavesurfer.js/dist/plugins/zoom.esm.js"
import { InformationCircleIcon } from "@heroicons/vue/24/solid"
import { nextTick, onMounted, onUnmounted, Ref, ref } from "vue"

const _SLIDER_MAX = 1000
const _MAX_ZOOM = 10000

const store = useAppStore()
const _zoomLevel = ref<number>(0)
const _waveSurferDivRef = ref<HTMLElement | null>(null)
const _ws = useWaveSurfer({ containerRef: _waveSurferDivRef, options: { normalize: true, autoCenter: true } })

// (@meersagor/wavesurfer-vue v2.0.2)
// Type could not be inferred here, so I fall back to an unsafe cast.
const _unsafeWaveSurfer = _ws.waveSurfer as Ref<any>
useWaveSurferTimeline({
  waveSurfer: _unsafeWaveSurfer,
  timelineOptions: { height: 32, timeInterval: 0.1, secondaryLabelInterval: 1.0 }
})
useWaveSurferMinimap({ waveSurfer: _unsafeWaveSurfer, minimapOptions: { height: 64 } })
useWaveSurferHover({
  waveSurfer: _unsafeWaveSurfer,
  hoverOptions: { labelSize: '1.5rem', formatTimeCallback: formatAudioPosition }
})

async function loadBlob(blob: Blob) {
  store.incrementBusyCounter()
  try {
    if (!_ws.waveSurfer.value) {
      throw new Error("waveSurfer must not be null.")
    }
    await _ws.waveSurfer.value.loadBlob(blob)

    // (wavesurfer.js v7.12.1)
    // The Zoom plugin crashes if it receives mouse‑wheel events before an audio is loaded.
    // Initialize the plugin only after WaveSurfer has finished loading an audio.
    const activePlugins = _ws.waveSurfer.value.getActivePlugins();
    const isZoomPluginLoaded = -1 != activePlugins.findIndex(p => "calculateNewZoom" in p)
    if (!isZoomPluginLoaded) {
      _ws.waveSurfer.value?.registerPlugin(new WaveSurferZoomPlugin({
        exponentialZooming: true,
        maxZoom: _MAX_ZOOM,
      }))
    }

    _ws.waveSurfer.value.seekTo(0)
    _updateZoomLevel()
  } finally {
    store.decrementBusyCounter()
  }
}

defineExpose({ loadBlob })

onMounted(async () => {
  await nextTick()

  window.addEventListener("keyup", _playPauseOnKeyUp)

  // Ensure that WaveSurfer fills the remaining space.
  const shadowRoot = _waveSurferDivRef.value?.querySelector(':scope >div')?.shadowRoot;
  if (!shadowRoot) {
    throw new Error("Assume that WaveSurfer has a shadowRoot.")
  }
  const styleElement = shadowRoot.querySelector('style')
  if (!styleElement) {
    throw new Error("Assume that WaveSurfer has a <style> element.")
  }
  styleElement.textContent += `
:where(.canvases, .progress) >div,
:where(.canvases, .progress) canvas {height: 100% !important}`;

  // (@meersagor/wavesurfer-vue v2.0.2)
  // "zoom" is not forwarded as a Vue event, so "@zoom" will never fire.
  _ws.waveSurfer.value?.on("zoom", (val) => {
    // logarithmic slider
    _zoomLevel.value = _SLIDER_MAX * Math.log(val) / Math.log(_MAX_ZOOM)
  })
})
onUnmounted(() => {
  window.removeEventListener("keyup", _playPauseOnKeyUp)
})

function _onZoomBarInput(event: InputEvent) {
  const el = event.target as HTMLInputElement
  _zoomLevel.value = parseFloat(el.value)
  _updateZoomLevel()
}
function _updateZoomLevel() {
  // logarithmic slider 
  _ws.waveSurfer.value?.zoom(Math.pow(_MAX_ZOOM, _zoomLevel.value / _SLIDER_MAX))
}

function _playPauseOnKeyUp(event: KeyboardEvent) {
  if (event.defaultPrevented) {
    // the event was already processed by another component.
    return
  }
  if (![" ", "Enter"].includes(event.key)) {
    return
  }
  if (event.target instanceof HTMLInputElement ||
    event.target instanceof HTMLButtonElement ||
    event.target instanceof HTMLSelectElement) {
    return
  }
  _ws.waveSurfer.value?.playPause()
}

</script>

<template>
  <div :class="$attrs.class" class="flex flex-col gap-2">
    <div v-if="_ws.isReady.value" class="flex flex-col md:flex-row landscape:flex-row gap-2">
      <div class="flex items-center gap-2">
        <button @click="_ws.waveSurfer.value?.playPause()" class="w-24 btn btn-primary">
          {{ _ws.isPlaying.value ? "Pause" : "Play" }}
        </button>
        <div class="join">
          <button type="button" @click="_ws.waveSurfer.value?.skip(-1)" class="btn join-item">-1s</button>
          <button type="button" @click="_ws.waveSurfer.value?.skip(+1)" class="btn join-item">+1s</button>
        </div>
        {{ formatAudioPosition(_ws.currentTime.value) }} / {{ formatAudioPosition(_ws.totalDuration.value) }}
      </div>
      <label class="input text-base-content">
        <span class="label">Zoom</span>
        <input type="range" @input="_onZoomBarInput" min="0" :max="_SLIDER_MAX" :value="_zoomLevel" class="range" />
      </label>
    </div>
    <div v-if="_ws.isReady.value" role="alert" class="hidden lg:grid alert alert-info text-info-content">
      <InformationCircleIcon class="w-6 h-6" />
      Press Space or Enter to play/pause the audio.
    </div>
    <div ref="_waveSurferDivRef" id="zs-waveform-controls" class="grow"></div>
  </div>
</template>
