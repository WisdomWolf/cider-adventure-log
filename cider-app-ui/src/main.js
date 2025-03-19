import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import axios from "axios";

axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL;


loadFonts()

createApp(App)
  .use(vuetify)
  .mount('#app')
