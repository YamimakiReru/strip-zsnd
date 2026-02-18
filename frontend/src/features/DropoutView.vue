<script setup lang="ts">
import { useAudioStore } from "@/stores/AudioStore";
import { useAppStore } from "@/stores/ZsndAppStore";
import { formatAudioPosition } from "@/util";

import WaveSurfer from "wavesurfer.js";
import { useWaveSurferRegions } from "@meersagor/wavesurfer-vue";
import { Ref, ref } from "vue";

const props = defineProps<{
  waveSurfer: WaveSurfer | null;
}>();
defineExpose({
  refresh,
});

const audioStore = useAudioStore();
const store = useAppStore();

const { regionsPlugin: _regionsPlugin } = useWaveSurferRegions({
  waveSurfer: ref(props.waveSurfer) as Ref<WaveSurfer | null>,
});

/**
 * Must be called explicitly by the parent view.
 * WaveSurfer loads and decodes audio asynchronously, so this component
 * cannot refresh itself automatically when the audio becomes available.
 */
async function refresh() {
  store.incrementBusyCounter();
  try {
    const sampleRate = audioStore.originalSampleRate;
    _regionsPlugin.value?.clearRegions();
    for (const [i, d] of audioStore.dropouts.entries()) {
      _regionsPlugin.value?.addRegion({
        content: `[${i + 1}]`,
        start: d.position / sampleRate,
        end: (d.position + d.duration) / sampleRate,
        color: "color-mix(in srgb, var(--color-error) 50%, transparent)",
        drag: false,
        resize: false,
      });
    }
  } finally {
    store.decrementBusyCounter();
  }
}
</script>

<template>
  <!-- By default, the daisyUI menu component uses flex-wrap, but I want the items to stay in a single column. -->
  <ul
    class="menu overflow-y-auto grow flex-nowrap portrait:h-0 portrait:w-full rounded-box"
  >
    <li v-for="(d, i) in audioStore.dropouts" :key="d.position">
      <a
        class="md:text-base"
        @click="
          waveSurfer?.setTime?.(d.position / audioStore.originalSampleRate)
        "
      >
        [{{ i + 1 }}]
        {{ formatAudioPosition(d.position / audioStore.originalSampleRate) }}
        -
        {{
          formatAudioPosition(
            (d.position + d.duration) / audioStore.originalSampleRate,
          )
        }}<wbr /> ({{ d.duration }} samples)
      </a>
    </li>
  </ul>
</template>
