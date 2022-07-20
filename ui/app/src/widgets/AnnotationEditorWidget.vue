<script setup>
import axios from 'axios'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { ref, computed, defineProps, onMounted } from 'vue'
import _ from 'lodash'

const $q = useQuasar()
const { t } = useI18n()

const props = defineProps({
  title: { type: String, default: null },
  endpoint: { type: String, required: true },
  field: { type: String, required: true },
  config: {
    type: Object,
    validator: val => !val || _.isObject(val),
    default: () => null,
  },
  readonly: { type: Boolean, default: false },
})

const loading = ref(true)
const data = ref(null)

const schema = computed(() => {
  const schema = []
  if (props.config) {
    for (const field of props.config) {
      schema.push({
        id: field.id,
        label: field.label ? t(field.label) : _.upperFirst(field.id).replaceAll('_', ' '),
        subLabel: field.subLabel ? t(field.subLabel) : null,
        style: 'font-weight: 500',
        ...componentByField(field),
      })
    }
  } else if (data.value[props.field]) {
    for (const [field_name, field_value] of Object.entries(data.value[props.field])) {
      console.log(field_name, field_value)
      schema.push({
        id: field_name,
        label: _.upperFirst(field_name).replaceAll('_', ' '),
        style: 'font-weight: 500',
        ...componentByValueType(field_value),
      })
    }
  }
  return schema
})

const componentByField = field => {
  const definition = { component: 'QInput' }
  if (field.type === 'Boolean') {
    definition.component = 'QCheckbox'
  } else if (field.type === 'Select') {
    definition.component = 'QSelect'
    definition.options = field.options
  }
  return definition
}

const componentByValueType = value => {
  const definition = { component: 'QInput' }
  if (_.isBoolean(value)) {
    definition.component = 'QCheckbox'
    // definition.type = 'checkbox'
  } else if (_.isNumber(value)) {
    definition.component = 'NumberInput'
    definition.type = 'number'
  } else if (_.isArray(value)) {
    definition.parseValue = val => `${JSON.stringify(val).substring(0, 50)}...`
    definition.parseInput = val => val.join(', ')
  } else if (_.isObject(value)) {
    console.log('is_object', value)
    definition.parseValue = val => `${JSON.stringify(val).substring(0, 50)}...`
  }
  return definition
}

const queryData = async () => {
  loading.value = true
  try {
    let { data: _data } = await axios.get(props.endpoint)
    data.value = _data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}
const save = async () => {
  try {
    const { status, statusText } = await axios.put(props.endpoint, data.value)
    if (status === 200) {
      $q.notify({
        type: 'positive',
        message: t('message.successfully_saved'),
      })
    } else {
      $q.notify({
        type: 'negative',
        message: `${t('error.cannot_save')} (${status}:${statusText})`,
      })
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  queryData()
})
</script>

<template>
  <div class="col q-px-md">
    <h6 v-if="props.title">{{ props.title }}</h6>
    <BlitzForm
      v-if="data"
      v-model="data[props.field]"
      :schema="schema"
      :column-count="3"
      :mode="props.readonly ? 'readonly' : 'edit'"
      :action-buttons="props.readonly ? [] : ['save', 'edit']"
      label-position="left"
      @save="save"
    />
  </div>
</template>

<script>
export default {
  name: 'AnnotationsEditorWidget',
}
</script>

<style scoped>
h6 {
  font-size: 20px;
  letter-spacing: 0.005em;
  font-weight: 400;
  text-align: left;
  margin-block-start: 0.1em;
  margin-block-end: 0.1em;
}
</style>
