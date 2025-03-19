import { createApp } from 'vue'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import App from './App.vue'
import { loadFonts } from './plugins/webfontloader'
import axios from "axios"


axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL;


loadFonts()

const vuetify = createVuetify({
  components,
  directives,
})

createApp(App)
  .use(vuetify)
  .mount('#app')
