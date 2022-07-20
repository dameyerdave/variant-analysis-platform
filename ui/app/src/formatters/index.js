import _ from 'lodash'
import { ellipsis as _ellipsis } from '../utils'

const vep_allele_string = value => {
  if (value.includes('/')) {
    const parts = value.split('/')
    return `${parts[0]}>${parts[1]}`
  }
  return value
}

const vep_strand = value => {
  if (value == -1) {
    return '-'
  } else if (value == 1) {
    return '+'
  } else {
    return value
  }
}

const beautify_list = values => {
  if (values) {
    const modified_values = []
    for (let v of values) {
      modified_values.push(beautify_string(v))
    }
    return modified_values.join(', ')
  }
  return values.join(', ')
}

const beautify_string = value => {
  if (value) {
    value = _.upperFirst(value.replaceAll('_', ' '))
  }
  return value
}

const ellipsis = value => {
  return _ellipsis(value, 50)
}

export default { vep_allele_string, vep_strand, beautify_list, beautify_string, ellipsis }
