const state = {
  locale: 'en',
}
const actions = {
  setLocale({ commit }, locale) {
    commit('SET_LOCALE', locale)
  },
}
const mutations = {
  SET_LOCALE(state, locale) {
    state.locale = locale
  },
}
const getters = {
  locale(state) {
    return state.locale
  },
}

export default {
  state,
  actions,
  mutations,
  getters,
}
