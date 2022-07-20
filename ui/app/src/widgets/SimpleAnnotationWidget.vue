<script setup>
import { defineProps, computed } from 'vue'
import formatters from '../formatters'
import DynamicValue from '../components/DynamicValue.vue'

const props = defineProps({
  annotations: {
    validator: prop => typeof prop === 'object' || prop === null || prop === undefined,
    required: true,
  },
  config: {
    type: Object,
    default: () => {
      return {}
    },
  },
  options: {
    type: Object,
    default: () => {
      return {
        na_string: 'N/A',
        label_fields: ['id', 'name', 'label'],
      }
    },
  },
})

const sorted_annotations = computed(() => {
  return Object.keys(props.annotations)
    .sort()
    .reduce((obj, key) => {
      obj[key] = props.annotations[key]
      return obj
    }, {})
})

const label = property => {
  if (
    props.config &&
    'annotations' in props.config &&
    property in props.config.annotations &&
    'label' in props.config.annotations[property]
  ) {
    return props.config.annotations[property].label
  } else {
    return property
  }
}
</script>

<template>
  <div class="q-pa-md row items-start q-gutter-sm">
    <template v-if="props.annotations">
      <template v-for="[key, value] in Object.entries(sorted_annotations)" :key="key">
        <q-card>
          <q-card-section class="q-py-xs bg-grey-3">
            <div class="text-bold" :title="key">
              {{ formatters.beautify_string(label(key)) }}
            </div>
          </q-card-section>
          <q-separator dark />
          <q-card-section class="q-py-xs">
            <DynamicValue
              :property="key"
              :value="value"
              :options="props.options"
              :config="props.config.annotations"
            />
          </q-card-section>
        </q-card>
      </template>
    </template>
  </div>
</template>

<script>
export default {
  name: 'SimpleAnnotationWidget',
}
</script>

<style scoped lang="sass">
ul.pointer
  list-style-type: '⇢'
  padding-left: 2px
  margin: 0
  li
    text-align: left
    padding-left: 2px
ul.no-bullets
  list-style-type: none
  padding: 0
  margin: 0
  li
    text-align: left
</style>
