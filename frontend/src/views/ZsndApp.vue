<script setup lang="ts">
import { useAudioStore } from "@/stores/AudioStore";
import WaveformControls from "@/features/WaveformControls.vue";
import ThemeChooser from "@/components/ThemeChooser.vue";
import LanguageChooser from "@/components/LanguageChooser.vue";
import ErrorBox from "@/components/ErrorBox.vue";
import LoadingIndicator from "@/components/LoadingIndicator.vue";

const audioStore = useAudioStore();

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
                <span class="label"
                  ><span class="hidden md:inline landscape:inline"
                    >ms</span
                  ></span
                >
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
                  >T<span class="hidden md:inline landscape:inline"
                    >hreshold</span
                  ></span
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
                <span class="label"
                  ><span class="hidden md:inline landscape:inline"
                    >dB</span
                  ></span
                >
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
