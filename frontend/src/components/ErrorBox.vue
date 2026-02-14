<script setup lang="ts">
import { useAppStore } from "@/stores/ZsndAppStore";
import { XCircleIcon } from "@heroicons/vue/24/solid";
const store = useAppStore();
</script>

<template>
  <TransitionGroup name="r-fade">
    <div
      v-for="(err, i) in store.errors"
      :key="i"
      role="alert"
      class="alert alert-error text-error-content"
      @click="store.removeErrorAt(i)"
    >
      <XCircleIcon class="w-6 h-6" />
      {{ err }}
    </div></TransitionGroup
  >
</template>
