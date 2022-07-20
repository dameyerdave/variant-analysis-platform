import axios from 'axios'
// import jwt_decode from 'jwt-decode'

const state = {
  jwt: localStorage.getItem('jwt'),
  refreshJwt: localStorage.getItem('refreshJwt'),
  user: JSON.parse(localStorage.getItem('user')),
  endpoints: {
    obtainJWT: '/auth/token/',
    refreshJWT: '/auth/refresh/',
    user: '/auth/users/me/',
  },
}
const actions = {
  async obtainToken({ state, commit, dispatch }, payload) {
    try {
      const resp = await axios.post(state.endpoints.obtainJWT, payload)
      commit('UPDATE_TOKEN', resp.data)
      dispatch('getUserInfo')
    } catch (err) {
      console.error(err)
    }
  },
  async getUserInfo({ state, commit }) {
    try {
      const resp = await axios.get(state.endpoints.user)
      commit('UPDATE_USER_INFO', resp.data)
    } catch (err) {
      console.error(err)
    }
  },
  async refreshJwt({ state, commit }) {
    const payload = {
      refresh: state.refreshJwt,
    }
    try {
      const resp = await axios.post(state.endpoints.refreshJWT, payload)
      commit('UPDATE_TOKEN', resp.data)
    } catch (err) {
      console.error(err)
    }
  },
  removeToken({ commit }) {
    commit('REMOVE_TOKEN')
    commit('REMOVE_USER_INFO')
  },
  // inspectToken({ state, dispatch }) {
  //   const token = state.jwt
  //   if (token) {
  //     const decoded = jwt_decode(token)
  //     const exp = decoded.exp
  //     const orig_iat = decoded.orig_iat
  //     if (exp - Date.now() / 1000 < 1800 && Date.now() / 1000 - orig_iat < 628200) {
  //       dispatch('refreshJwt')
  //     } else if (exp - Date.now() / 1000 < 1800) {
  //       // DO NOTHING, DO NOT REFRESH
  //     } else {
  //       // PROMPT USER TO RE-LOGIN, THIS ELSE CLAUSE COVERS THE CONDITION WHERE A TOKEN IS EXPIRED AS WELL
  //     }
  //   }
  // },
}
const mutations = {
  UPDATE_TOKEN(state, payload) {
    localStorage.setItem('jwt', payload.access)
    state.jwt = payload.access
    if (payload.refresh) {
      localStorage.setItem('refreshJwt', payload.refresh)
      state.refreshJwt = payload.refresh
    }
  },
  REMOVE_TOKEN(state) {
    localStorage.removeItem('jwt')
    localStorage.removeItem('refreshJwt')
    state.jwt = null
    state.refreshJwt = null
    state.user = null
  },
  UPDATE_USER_INFO(state, payload) {
    localStorage.setItem('user', JSON.stringify(payload))
    state.user = payload
  },
  REMOVE_USER_INFO(state) {
    localStorage.removeItem('user')
    state.user = null
  },
}
const getters = {
  jwt(state) {
    return state.jwt
  },
  refreshJwt(state) {
    return state.refreshJwt
  },
  user(state) {
    return state.user
  },
}

export default {
  state,
  actions,
  mutations,
  getters,
}
