<script setup lang="ts">
import { PaintBrushIcon } from "@heroicons/vue/16/solid";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const props = defineProps<{ defaultTheme?: string }>();

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
</script>

<template>
  <li>
    <details>
      <summary>
        <PaintBrushIcon class="w-4 h-4" />{{ t("app.theme") }}
      </summary>
      <ul>
        <li v-for="theme of _DAISYUI_THEMES" :key="theme">
          <input
            type="radio"
            name="theme-dropdown"
            class="theme-controller btn btn-block btn-ghost"
            :aria-label="theme"
            :value="theme"
            :checked="defaultTheme === theme"
          />
        </li>
      </ul>
    </details>
  </li>
</template>
