import ZsndApp from "@/views/ZsndApp.vue";

import { createI18n } from "vue-i18n";
import { createPinia } from "pinia";
import { createApp, App } from "vue";

declare global {
  const _MESSAGES: Record<string, any>;
}

function _initI18n(app: App) {
  let locale = "en";
  for (const localeId of navigator.languages) {
    if (localeId in _MESSAGES) {
      locale = localeId;
      break;
    }
    const lang = localeId.split("-")[0];
    if (lang in _MESSAGES) {
      locale = lang;
      break;
    }
  }

  const i18n = createI18n({
    legacy: false,
    locale,
    fallbackLocale: "en",
    messages: _MESSAGES,
  });
  app.use(i18n);
}

const theApp = createApp(ZsndApp);
_initI18n(theApp);
theApp.use(createPinia());
theApp.mount("#zs-app");
