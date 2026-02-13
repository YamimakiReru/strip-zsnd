import { createApp } from "vue"
import { createPinia } from "pinia"
import ZsndApp from "@/views/ZsndApp.vue"

const app = createApp(ZsndApp)
app.use(createPinia())
app.mount("#zs-app")
