import { createApp } from 'vue'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import './assets/fonts.css'
import App from './App.vue'
import {
  cellarDark, cellarLight,
  ledgerDark, ledgerLight,
  tastingNotesDark, tastingNotesLight,
  initialTheme,
} from './theme'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: initialTheme(),
    themes: {
      tastingNotesLight,
      tastingNotesDark,
      cellarLight,
      cellarDark,
      ledgerLight,
      ledgerDark,
    },
  },
  defaults: {
    VCard: { rounded: 'lg' },
    VBtn: { rounded: 'lg' },
    VChip: { rounded: 'lg' },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VTextarea: { variant: 'outlined', density: 'comfortable' },
    VSelect: { variant: 'outlined', density: 'comfortable' },
    VCombobox: { variant: 'outlined', density: 'comfortable' },
    VFileInput: { variant: 'outlined', density: 'comfortable' },
  },
})

createApp(App)
  .use(vuetify)
  .mount('#app')
