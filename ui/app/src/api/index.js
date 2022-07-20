import axios from 'axios'
import store from '../store'

export default {
  meta: async endpoint => {
    console.debug('OPTIONS:', endpoint)
    let { data } = await axios.options(endpoint)
    return data
  },
  query: async endpoint => {
    console.debug('GET:', endpoint)
    const { data } = await axios.get(endpoint, {
      params: { filter: store.getters.filter },
    })
    if (!data.results) {
      return { count: 1, next: null, previous: null, results: [data] }
    } else {
      return data
    }
  },
}
