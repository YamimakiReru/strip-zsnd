<script setup lang="ts">
import { LanguageIcon } from "@heroicons/vue/16/solid";
import { useI18n } from "vue-i18n";

const { locale, availableLocales, t } = useI18n();
</script>

<template>
  <li>
    <details>
      <summary>
        <LanguageIcon class="w-4 h-4" />Language
      </summary>
      <ul>
        <li v-for="lc in availableLocales" :key="lc">
          <input
            type="radio"
            class="btn btn-block btn-ghost"
            :aria-label="t('app.locale_name', {}, { locale: lc })"
            :value="lc"
            :checked="locale === lc"
            @change="locale = lc"
          />
        </li>
      </ul>
    </details>
  </li>
</template>
