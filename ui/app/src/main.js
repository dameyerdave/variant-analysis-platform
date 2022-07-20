// FILE: main.js

import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import messages from '@intlify/vite-plugin-vue-i18n/messages'

import router from './router'
import store from './store'

import axios from 'axios'
import VueAxios from 'vue-axios'

import { Quasar, Notify, LoadingBar, Dialog } from 'quasar'
import quasarIconSet from 'quasar/icon-set/bootstrap-icons'

// Import icon libraries
import '@quasar/extras/roboto-font-latin-ext/roboto-font-latin-ext.css'
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/line-awesome/line-awesome.css'
import '@quasar/extras/bootstrap-icons/bootstrap-icons.css'

// A few examples for animations from Animate.css:
import '@quasar/extras/animate/fadeIn.css'
import '@quasar/extras/animate/fadeOut.css'

// Import Quasar css
import 'quasar/src/css/index.sass'

// Import Blizar css
import { BlitzForm } from 'blitzar'
import 'blitzar/dist/style.css'

// Import own global components
import NumberInput from './components/NumberInput.vue'

// Assumes your root component is App.vue
// and placed in same folder as main.js
import App from './App.vue'

const i18n = createI18n({
  locale: store.getters.locale,
  fallbackLocale: 'en',
  messages,
})

axios.defaults.headers = {
  'Cache-Control': 'no-cache',
  'Pragma': 'no-cache',
  'Expires': '0',
}
axios.defaults.baseURL = `${import.meta.env.VITE_APP_BACKEND}/api`

axios.interceptors.request.use(
  config => {
    const token = store.getters.jwt
    if (token) {
      config.headers.Authorization = `JWT ${token}`
    }
    LoadingBar.start()
    return config
  },
  error => {
    console.error('AXIOS request error:', error.response)
    Notify.create({
      message: error,
      caption: 'Request error',
      icon: 'warning',
      color: 'warning',
    })
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => {
    LoadingBar.stop()
    return response
  },
  async error => {
    LoadingBar.stop()
    const originalConfig = error.config
    console.debug('originalConfig', originalConfig)
    if (
      error.response.status === 401 &&
      !originalConfig._retry &&
      originalConfig.url !== '/auth/refresh/' &&
      store.getters.refreshJwt
    ) {
      // In case the token has expired we try to refresh the token
      originalConfig._retry = true
      console.debug('refreshJwt')
      await store.dispatch('refreshJwt')
      // Resend the request with the refreshed token
      return axios(originalConfig)
    } else if (error.response.status === 401 && originalConfig._retry) {
      // If the token cannot be refreshed we logout and route to the login page
      console.debug('logout')
      store.dispatch('removeToken')
      router.push({ path: '/login' })
    } else if (error.response) {
      Notify.create({
        message: `${error.response.data.detail || error.response.data.non_field_errors}`,
        multiLine: true,
        caption: `${error.response.config.url}: ${error.response.status}: ${error.response.statusText}`,
        icon: 'warning',
        color: 'negative',
      })
    } else {
      Notify.create({
        message: 'Response error',
        multiLine: true,
        caption: `${error}`,
        icon: 'warning',
        color: 'negative',
      })
    }

    console.error('AXIOS reponse error:', error)
    return Promise.reject(error)
  }
)

const app = createApp(App)

app.component('BlitzForm', BlitzForm)
app.component('NumberInput', NumberInput)

app.use(VueAxios, axios)
app.use(i18n)
app.use(store)
app.use(router)

app.use(Quasar, {
  plugins: {
    Notify,
    LoadingBar,
    Dialog,
  },
  config: {
    brand: {
      'primary': '#1976d2',
      'secondary': '#26A69A',
      'accent': '#9C27B0',

      'dark': '#1d1d1d',
      'dark-page': '#121212',

      'positive': '#21BA45',
      'negative': '#C10015',
      'info': '#31CCEC',
      'warning': '#F2C037',
    },
    notify: {},
    loadingBar: {
      color: 'light-blue-5',
      size: '5px',
      position: 'top',
    },
  },
  iconSet: quasarIconSet,
})

// Assumes you have a <div id="app"></div> in your index.html
app.mount('#app')
