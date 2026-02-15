<script setup lang="ts">
import { LanguageIcon } from "@heroicons/vue/24/solid";
import { useI18n } from "vue-i18n";

const { locale, availableLocales, t } = useI18n();
</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn btn-sm md:btn-md">
      <LanguageIcon class="w-6 h-6" />
    </div>
    <ul
      tabindex="-1"
      class="dropdown-content overflow-y-scroll max-h-[80vh] bg-base-300 text-base-content rounded-box z-10 w-32 p-2 shadow-2xl"
    >
      <li v-for="lc in availableLocales" :key="lc">
        <input
          type="radio"
          class="w-full btn btn-block btn-ghost justify-start"
          :aria-label="t('app.locale_name', {}, { locale: lc })"
          :value="lc"
          :checked="locale === lc"
          @change="locale = lc"
        />
      </li>
    </ul>
  </div>
</template>
