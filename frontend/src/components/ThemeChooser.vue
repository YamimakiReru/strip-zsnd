<script setup lang="ts">
import { PaintBrushIcon, ChevronDownIcon } from "@heroicons/vue/24/solid";
import { useI18n } from "vue-i18n";

const _DEFAULT_THEME = "synthwave";

const _DAISYUI_THEMES = [
  "light",
  "dark",
  "cupcake",
  "bumblebee",
  "emerald",
  // ----
  "corporate",
  "synthwave",
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
];

const { t } = useI18n();
</script>

<template>
  <div class="dropdown">
    <div tabindex="0" role="button" class="btn btn-sm md:btn-md min-w-28">
      <PaintBrushIcon class="w-6 h-6 hidden sm:block" />
      {{ t("app.theme") }}
      <ChevronDownIcon class="w-6 h-6" />
    </div>
    <ul
      tabindex="-1"
      class="dropdown-content overflow-y-scroll max-h-[80vh] bg-base-300 text-base-content rounded-box z-10 w-52 p-2 shadow-2xl"
    >
      <li v-for="theme of _DAISYUI_THEMES" :key="theme">
        <input
          type="radio"
          name="theme-dropdown"
          class="theme-controller w-full btn btn-sm btn-block btn-ghost justify-start"
          :aria-label="theme"
          :value="theme"
          :checked="_DEFAULT_THEME === theme"
        />
      </li>
    </ul>
  </div>
</template>
