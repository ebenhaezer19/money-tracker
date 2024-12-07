import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { initAuth } from './stores/initAuth'

const app = createApp(App)
const pinia = createPinia()

// Install plugins
app.use(pinia)
app.use(router)

// Init auth setelah pinia terpasang
initAuth()

// Mount app
app.mount('#app') 