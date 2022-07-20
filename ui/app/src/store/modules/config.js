import axios from 'axios'

const state = {
  config: {},
}
const actions = {
  async loadConfig({ commit }) {
    try {
      let { data } = await axios.get('/config/')
      commit('SET_CONFIG', data)
    } catch (err) {
      console.error(err)
    }
  },
}
const mutations = {
  SET_CONFIG(state, config) {
    state.config = config
  },
}
const getters = {
  config(state) {
    return state.config
  },
}

export default {
  state,
  actions,
  mutations,
  getters,
}
