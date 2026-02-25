<script setup lang="ts">
import { useAudioStore } from "@/stores/AudioStore";
import ThemeChooser from "@/components/ThemeChooser.vue";
import LanguageChooser from "@/components/LanguageChooser.vue";

import {
  ArrowDownOnSquareIcon,
  ArrowTopRightOnSquareIcon,
  MoonIcon as MoonIcon16,
  ScissorsIcon,
} from "@heroicons/vue/16/solid";
import { MoonIcon as MoonIcon24 } from "@heroicons/vue/24/solid";
import { useI18n } from "vue-i18n";
import { computed, ref } from "vue";

const { t } = useI18n();
const audioStore = useAudioStore();

const _VERSION = __APP_VERSION__;

const _aboutDialog = ref<HTMLDialogElement | null>(null);

const _downloadFilename = computed(() => {
  if (!audioStore.originalFilename) {
    return "audio.wav";
  } else {
    const dotPos = audioStore.originalFilename.lastIndexOf(".");
    return -1 == dotPos
      ? `${audioStore.originalFilename}-fix.wav`
      : `${audioStore.originalFilename.substring(0, dotPos)}-fix.wav`;
  }
});

const _downloadUrl = computed(() => {
  if (audioStore.audioBlobForPreview) {
    return URL.createObjectURL(audioStore.audioBlobForPreview);
  } else {
    return null;
  }
});
</script>

<template>
  <div class="dropdown">
    <div
      :title="t('app.system_menu')"
      tabindex="0"
      role="button"
      class="btn btn-sm md:btn-md btn-neutral text-neutral-content"
    >
      <MoonIcon16 class="w-4 h-4 md:hidden" />
      <MoonIcon24 class="w-6 h-6 hidden md:block" />
    </div>
    <ul
      tabindex="-1"
      class="dropdown-content menu flex-nowrap overflow-y-scroll max-h-[80vh] min-w-60 bg-base-100 rounded-box z-10 p-2 shadow-2xl"
    >
      <li :class="{ 'menu-disabled': null == audioStore.audioBlobForPreview }">
        <a :download="_downloadFilename" :href="_downloadUrl">
          <ArrowDownOnSquareIcon class="w-4 h-4" />{{ t("app.save") }}
        </a>
      </li>
      <li :class="{ 'menu-disabled': null == audioStore.audioBlobForPreview }">
        <a @click="audioStore.trimAllDropouts()"
          ><ScissorsIcon class="w-4 h-4" />{{ t("zend.trim_all_dropouts") }}</a
        >
      </li>
      <hr class="my-2" />
      <LanguageChooser />
      <ThemeChooser default-theme="synthwave" />
      <li><a @click="_aboutDialog?.showModal()">About</a></li>
    </ul>
    <dialog ref="_aboutDialog" class="modal">
      <div class="modal-box">
        <h3 class="text-lg font-bold">
          <MoonIcon24 class="w-6 h-6 inline" />
          {{ t("app.title") }}
        </h3>
        <p class="pt-4 text-right">
          <a
            class="link"
            href="https://github.com/YamimakiReru/strip-zsnd"
            target="_blank"
            ><ArrowTopRightOnSquareIcon class="w-4 h-4 inline" />
            https://github.com/YamimakiReru/strip-zsnd</a
          ><br />
          Copyright (c) 2026
          <a
            class="link"
            href="https://gravatar.com/happilybeliever334e7100d5"
            target="_blank"
            >YAMIMAKI, Reru</a
          >
        </p>
        <p class="pt-4 text-right">
          Licensed under the MIT License.<br />
          Version {{ _VERSION }}
        </p>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn">OK</button>
          </form>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button>OK</button>
      </form>
    </dialog>
  </div>
</template>
