import { createStore } from 'vuex'
import config from './modules/config.js'
import locale from './modules/locale.js'
import filter from './modules/filter.js'
import user from './modules/user.js'

const store = createStore({
  modules: {
    config,
    locale,
    filter,
    user,
  },
})

export default store
