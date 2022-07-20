const state = {
  filter: localStorage.getItem('filter', 'default'),
}
const actions = {
  setFilter({ commit }, filter) {
    commit('SET_FILTER', filter)
  },
}
const mutations = {
  SET_FILTER(state, filter) {
    localStorage.setItem('filter', filter)
    state.filter = filter
  },
}
const getters = {
  filter(state) {
    return state.filter
  },
}

export default {
  state,
  actions,
  mutations,
  getters,
}
