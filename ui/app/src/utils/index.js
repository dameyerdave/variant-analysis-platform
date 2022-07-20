import _ from 'lodash'
import store from '../store'

const ellipsis = (value, max_length = 30, na_string = 'N/A') => {
  if (!value) {
    return na_string
  }
  if (_.isString(value)) {
    if (value.length > max_length) {
      return `${value.substring(0, max_length - 3)}...`
    }
  }
  if (_.isObject(value)) {
    return `${JSON.stringify(value).substring(0, max_length - 3)}...`
  }
  return value
}

// Returns a url with the reference or
const referenciate = (value, reference = null) => {
  const ref_configs = store.getters.config.references
  value = String(value)
  if (reference) {
    return value.replace(/(.*)/, reference)
  } else {
    for (const ref_config of ref_configs) {
      const regex = new RegExp(ref_config.regex, 'g')
      if (regex.test(value)) {
        return value.replace(regex, ref_config.url)
      }
    }
  }
  return null
}

const onInactivity = (timeoutInMin, callback) => {
  let timeoutId = null

  const startTimer = () => {
    timeoutId = setTimeout(callback, timeoutInMin * 60 * 1000)
  }

  const resetTimer = () => {
    clearTimeout(timeoutId)
    startTimer()
  }

  document.addEventListener('keypress', resetTimer, false)
  document.addEventListener('mousemove', resetTimer, false)
  document.addEventListener('mousedown', resetTimer, false)
  document.addEventListener('touchmove', resetTimer, false)

  startTimer()
}

export { ellipsis, referenciate, onInactivity }
