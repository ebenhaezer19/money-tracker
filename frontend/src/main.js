import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Buat instance aplikasi Vue
const app = createApp(App)

// Pasang Pinia
const pinia = createPinia()
app.use(pinia)

// Pasang router
app.use(router)

// Mount aplikasi
app.mount('#app') 