<script setup lang="ts">
import { useAppStore } from "@/stores/ZsndAppStore";
import { computed } from "vue";
const store = useAppStore();
const isBusy = computed(() => store.isBusy);
const progress = computed(() => store.progress);
</script>

<template>
  <!--
  Enable container queries to specify the radial progress --size using the cqmin unit.
  In daisyUI v5.5.18, using the % unit breaks daisyUI's internal CSS calculations.
-->
  <div
    v-if="isBusy"
    class="z-50 @container-[size] absolute inset-0 flex justify-center items-center bg-neutral/50"
  >
    <div class="w-[80cqmin] h-[80cqmin]">
      <div
        v-if="null != progress"
        class="radial-progress text-primary text-[8vmin] m-auto"
        role="progressbar"
        :style="{
          '--value': progress,
        }"
        style="--size: 80cqmin; --thickness: 2rem"
        aria-valuenow="progress"
      >
        {{ progress }}%
      </div>
      <div v-else class="loading loading-spinner w-full text-primary"></div>
    </div>
  </div>
</template>
