<script setup lang="ts">
import { useAudioStore } from "@/stores/AudioStore";
import { useAppStore } from "@/stores/ZsndAppStore";
import { formatAudioPosition } from "@/util";

import WaveSurfer from "wavesurfer.js";
import { useWaveSurferRegions } from "@meersagor/wavesurfer-vue";
import { watch } from "vue";

const props = defineProps<{
  waveSurfer: WaveSurfer | null;

  /**
   * Vue wrapper for the `@meersagor/wavesurfer-vue` version of the
   * WaveSurfer Regions plugin.
   *
   * (In 2.0.2)
   * This component requires the WaveSurfer instance to already exist
   * before the component is mounted.
   *
   * In Vue, child components mount before their parents, so a plugin
   * wrapper cannot create its plugin during onMounted if the parent
   * hasn't finished creating WaveSurfer yet.
   *
   * Therefore, plugin initialization must happen in the parent (or any
   * ancestor) that owns the WaveSurfer instance.
   */
  regionsPlugin: ReturnType<
    typeof useWaveSurferRegions
  >["regionsPlugin"]["value"];
}>();

const audioStore = useAudioStore();
const store = useAppStore();

watch(
  () => [audioStore.dropouts, props.waveSurfer?.getDuration?.()],
  // This code assumes that getDuration() returns 0 or a shorter value before loading completes.
  ([dropouts, isReady]) => {
    store.incrementBusyCounter();
    try {
      const sampleRate = audioStore.originalSampleRate;
      props.regionsPlugin?.clearRegions();
      if (!isReady) {
        return;
      }
      for (const [i, d] of (dropouts as any).entries()) {
        props.regionsPlugin?.addRegion({
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
  },
);
</script>

<template>
  <!-- By default, the daisyUI menu component uses flex-wrap, but I want the items to stay in a single column. -->
  <ul
    class="menu flex-nowrap overflow-y-auto rounded-box"
    :class="$attrs.class"
  >
    <li v-for="(d, i) in audioStore.dropouts" :key="d.position">
      <a
        class="md:text-base"
        @click="
          props.waveSurfer?.setTime?.(
            d.position / audioStore.originalSampleRate,
          )
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
