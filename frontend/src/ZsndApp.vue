<script setup lang="ts">
import { useWaveSurfer, useWaveSurferTimeline, useWaveSurferMinimap } from "@meersagor/wavesurfer-vue"
import WaveSurferZoomPlugin from "wavesurfer.js/dist/plugins/zoom.esm.js"
import { XCircleIcon, InformationCircleIcon, PaintBrushIcon, ChevronDownIcon } from "@heroicons/vue/24/solid"
import { onMounted, onUnmounted, ref } from "vue"

const SLIDER_MAX = 1000
const MAX_ZOOM = 10000

const DAISYUI_THEMES = [
  "synthwave",
  // ----
  "light",
  "dark",
  "cupcake",
  "bumblebee",
  "emerald",
  // ----
  "corporate",
  "retro",
  "cyberpunk",
  "valentine",
  // ----
  "helloween",
  "garden",
  "forest",
  "aqua",
  "lofi",
  // ----
  "pastel",
  "fantasy",
  "wireframe",
  "black",
  "luxury",
  // ----
  "dracula",
  "cmyk",
  "autumn",
  "business",
  "acid",
  // ----
  "lemonade",
  "night",
  "coffee",
  "winter",
  "dim",
  // ----
  "nord",
  "sunset",
  "caramelatte",
  "abyss",
  "silk",
]

const isBlocking = ref<boolean>(false)
const selectedFile = ref<File | null>(null)
const fileLoadingError = ref<string | null>(null)
const zoomLevel = ref<number>(0)

const el = ref<HTMLElement | null>(null)
const waveSurferDivRef = ref<HTMLElement | null>(null)
const timelineContainerRef = ref<HTMLElement | null>(null)
const minimapContainerRef = ref<HTMLElement | null>(null)
const { waveSurfer, isReady, totalDuration, isPlaying, currentTime }
  = useWaveSurfer({ containerRef: waveSurferDivRef, options: { height: window.innerHeight * 0.7 } })
const { timelinePlugin } = useWaveSurferTimeline({
  // @ts-ignore-
  waveSurfer,
  // @ts-ignore-
  timelineOptions: { height: 32, secondaryLabelInterval: 0.1, container: timelineContainerRef.value }
})
const { minimapPlugin } = useWaveSurferMinimap({
  // @ts-ignore-
  waveSurfer,
  // @ts-ignore-
  minimapOptions: { height: 64, container: minimapContainerRef.value }
})

// Make WaveSurfer responsive to container resize.
let observer: ResizeObserver | null = null
onMounted(() => {
  observer = new ResizeObserver(async () => {
    setTimeout(() => {
      waveSurfer.value?.setOptions({ height: window.innerHeight * 0.7 })
    }, 100);
  })
  el.value && observer.observe(el.value)
  window.addEventListener("keyup", playPauseOnKeyUp)
  waveSurfer.value?.on("zoom", (val) => {
    // logarithmic slider
    zoomLevel.value = SLIDER_MAX * Math.log(val) / Math.log(MAX_ZOOM)
  })
})
onUnmounted(() => {
  window.removeEventListener("keyup", playPauseOnKeyUp)
  observer?.disconnect()
})

function onZoomBarInput(event: InputEvent) {
  // logarithmic slider 
  // @ts-ignore
  waveSurfer.value?.zoom(Math.pow(MAX_ZOOM, event.target?.value / SLIDER_MAX))
}
function onFileChange(event: Event) {
  const inputElement = event.target as HTMLInputElement
  selectedFile.value = inputElement.files?.[0] || null
}

async function onLoadFile(event: Event) {
  if (!selectedFile.value) {
    fileLoadingError.value = "Please select a file to detect dropouts."
    return
  }
  isBlocking.value = true
  try {
    const blob = await selectedFile.value.slice()
    await waveSurfer.value?.loadBlob(blob)
    if (!waveSurfer.value) {
      throw new Error("waveSurfer must not be null.")
    }

    // (wavesurfer.js v7.12.1)
    // The Zoom plugin crashes if it receives mouse‑wheel events before an audio is loaded.
    // Initialize the plugin only after WaveSurfer has finished loading an audio.
    const isZoomPluginLoaded =
      -1 != waveSurfer.value.getActivePlugins().findIndex((p: any) => p.calculateNewZoom)
    if (!isZoomPluginLoaded) {
      waveSurfer.value?.registerPlugin(new WaveSurferZoomPlugin({
        exponentialZooming: true,
        maxZoom: MAX_ZOOM,
      }))
    }
  } catch (exc) {
    console.error(exc)
    const msg = exc instanceof Error ? exc.message : String(exc)
    fileLoadingError.value = `Could not load file: ${msg}`
  } finally {
    isBlocking.value = false
  }
}

function playPauseOnKeyUp(event: KeyboardEvent) {
  if (![" ", "Enter"].includes(event.key)) {
    return
  }
  if (event.target instanceof HTMLInputElement) {
    return
  }
  waveSurfer.value?.playPause()
}

/**
 * @returns {string} e.g. "01:23.456"
 */
function formatAudioPosition(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const millis = Math.floor((seconds % 1) * 1000)
  return (
    String(minutes).padStart(2, "0") +
    ":" + String(secs).padStart(2, "0") +
    "." + String(millis).padStart(3, "0")
  )
}
</script>

<template>
  <div ref="el" class="inset-0 p-4">
    <!-- loading spinner -->
    <div v-if="isBlocking" class="z-50 fixed inset-0 bg-neutral/20 flex items-center justify-center">
      <div class="loading loading-spinner loading-xl -scale-500 text-primary"></div>
    </div>
    <!-- body -->
    <div class="max-w-5xl mx-auto p-4 bg-neutral rounded-lg">
      <div>
        <div class="join">
          <input type="file" @change="onFileChange" accept=".wav" class="file-input join-item" />
          <button type="button" @click="onLoadFile" :disabled="!selectedFile"
            class="btn btn-secondary join-item">Detect</button>
        </div>
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn m-1">
            <PaintBrushIcon class="w-6 h-6" />
            Theme
            <ChevronDownIcon class="w-6 h-6" />
          </div>
          <ul tabindex="-1" class="dropdown-content bg-base-300 rounded-box z-10 w-52 p-2 shadow-2xl">
            <li v-for="theme of DAISYUI_THEMES" :key="theme">
              <input type="radio" name="theme-dropdown"
                class="theme-controller w-full btn btn-sm btn-block btn-ghost justify-start" :aria-label="theme"
                :value="theme" :checked="'synthwave' == theme" />
            </li>
          </ul>
        </div>
        <transition name="r-fade">
          <div role="alert" class="alert alert-error mt-4" v-if="fileLoadingError" @click="fileLoadingError = null">
            <XCircleIcon class="w-6 h-6" />
            {{ fileLoadingError }}
          </div>
        </transition>
        <div v-if="isReady" class="mt-4">
          <button @click="waveSurfer?.playPause()" class="btn btn-primary">
            {{ isPlaying ? "Pause" : "Play" }}
          </button>
          {{ formatAudioPosition(currentTime) }} / {{ formatAudioPosition(totalDuration) }}
          <button type="button" @click="waveSurfer?.skip(-1)" class="btn">-1s</button>
          <button type="button" @click="waveSurfer?.skip(+1)" class="btn">+1s</button>
          &nbsp;Zoom&nbsp;
          <input type="range" @input="onZoomBarInput" min="0" :max="SLIDER_MAX" :value="zoomLevel" class="range" />
        </div>
        <div v-if="isReady" role="alert" class="alert alert-info alert-soft mt-4">
          <InformationCircleIcon class="w-6 h-6" />
          Press Space or Enter to play/pause the audio.
        </div>
        <div ref="waveSurferDivRef"></div>
        <div ref="timelineContainerRef"></div>
        <div ref="minimapContainerRef"></div>
      </div>
    </div>
  </div>
</template>
