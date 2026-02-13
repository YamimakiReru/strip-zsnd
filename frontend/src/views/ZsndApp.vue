<script setup lang="ts">
import { useAppStore } from "@/stores/ZsndAppStore.ts"
import WaveformControls from "@/features/WaveformControls.vue"
import ThemeChooser from "@/components/ThemeChooser.vue"

import { XCircleIcon } from "@heroicons/vue/24/solid"
import { ref } from "vue"

const store = useAppStore()
const _fileLoadingError = ref<string | null>(null)
const _waveformControls = ref<InstanceType<typeof WaveformControls> | null>(null)

async function _onFileChange(event: Event) {
  const inputElement = event.target as HTMLInputElement
  const selectedFile = inputElement.files?.[0]
  if (!selectedFile) {
    return
  }

  store.incrementBusyCounter()
  try {
    await _waveformControls.value?.loadBlob(selectedFile)

    // Blur the focus to prevent the file from reloading
    // when the user presses Enter repeatedly.
    if (event.target instanceof HTMLElement) {
      event.target.blur()
    }
  } catch (exc) {
    console.error(exc)
    const msg = exc instanceof Error ? exc.message : String(exc)
    _fileLoadingError.value = `Could not load file: ${msg}`
  } finally {
    store.decrementBusyCounter()
  }
}
</script>

<template>
  <div ref="el" class="fixed inset-0 md:p-4">
    <!-- loading spinner -->
    <div v-if="store.isBusy" class="z-50 fixed inset-0 bg-neutral/50 flex items-center justify-center">
      <div class="loading loading-spinner loading-xl -scale-500 text-primary"></div>
    </div>
    <!-- body -->
    <div class="w-full h-full flex flex-col gap-2 max-w-5xl mx-auto p-2 bg-neutral text-neutral-content rounded-lg">
      <div class="flex gap-2">
        <input type="file" @change="_onFileChange" accept=".wav"
          class="file-input file-input-sm md:file-input-md text-base-content/50" />
        <ThemeChooser />
      </div>
      <transition name="r-fade">
        <div role="alert" class="alert alert-error text-error-content" v-if="_fileLoadingError"
          @click="_fileLoadingError = null">
          <XCircleIcon class="w-6 h-6" />
          {{ _fileLoadingError }}
        </div>
      </transition>
      <WaveformControls ref="_waveformControls" class="grow" />
    </div>
  </div>
</template>
