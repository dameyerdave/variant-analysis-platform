<script setup>
import { defineProps, computed, defineAsyncComponent } from 'vue'
import _ from 'lodash'
import { v4 as uuid } from 'uuid'
import { ellipsis, referenciate } from '../utils'
import ReferencedQTree from './ReferencedQTree.vue'
import { openURL } from 'quasar'

const props = defineProps({
  property: {
    type: String,
    required: true,
  },
  value: {
    // we accept all kind of values
    validator: () => true,
    required: true,
  },
  config: {
    validator: value => value === undefined || value === null || typeof value === 'object',
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

const getLabel = (key, value) => {
  if (value === null) {
    return key
  }
  if (_.isNumber(key)) {
    return '⇢'
  }
  if ('label_fields' in props.options && _.isObject(value)) {
    for (const field of props.options.label_fields) {
      if (field in value) {
        return value[field]
      }
    }
  }
  return key
}

const getReference = val => {
  let reference = null
  if (_.isNumber(val) || _.isString(val)) {
    if (props.config && props.property in props.config && 'reference' in props.config[props.property]) {
      reference = props.config[props.property].reference
    }
  }
  return referenciate(val, reference)
}

const addNodes = (node, value) => {
  if (_.isNumber(value) || _.isString(value)) {
    node.push({
      key: uuid(),
      label: value,
      reference: getReference(value),
    })
  } else if (_.isObject(value)) {
    for (const [key, val] of Object.entries(value)) {
      if (_.isNumber(val) || _.isString(val)) {
        let label = `${key}: ${val}`
        if (!isNaN(key)) {
          if (value.length === 1) {
            label = val
          } else {
            label = `⇢ ${val}`
          }
        }
        node.push({
          key: uuid(),
          label,
          reference: getReference(val),
        })
      } else {
        node.push({
          key: uuid(),
          label: getLabel(key, val),
          children: addNodes([], val),
        })
      }
    }
  }
  return node
}

const nodes = computed(() => {
  return addNodes([], props.value)
})

const comp = computed(() => {
  if (props.config && props.property in props.config && 'component' in props.config[props.property]) {
    return defineAsyncComponent(() =>
      import(`../widgets/annotation/${props.config[props.property].component}.vue`)
    )
  } else {
    return null
  }
})

const compConfig = computed(() => {
  if (props.config && props.property in props.config && 'config' in props.config[props.property]) {
    return props.config[props.property].config
  } else {
    return null
  }
})
</script>

<template>
  <template v-if="comp">
    <component :is="comp" :value="props.value" :config="compConfig" :options="options" />
  </template>
  <template v-else-if="_.isArray(props.value) && props.value.length === 1 && _.isString(props.value[0])">
    <a v-if="(reference = getReference(props.value[0]))" @click="openURL(reference)">
      {{ ellipsis(props.value[0], 50, props.options.na_string) }}
    </a>
    <template v-else>
      {{ ellipsis(props.value[0], 50, props.options.na_string) }}
    </template>
  </template>
  <template v-else-if="_.isNumber(props.value) || _.isString(props.value)">
    <a v-if="(reference = getReference(props.value))" @click="openURL(reference)">
      {{ ellipsis(props.value, 50, props.options.na_string) }}
    </a>
    <template v-else>
      {{ ellipsis(props.value, 50, props.options.na_string) }}
    </template>
  </template>
  <template v-else>
    <q-list v-if="nodes.length > 3">
      <q-expansion-item dense expand-separator class="no-border">
        <template #header>
          <q-item-section> {{ nodes[0].label }}... </q-item-section>
        </template>
        <q-card>
          <q-card-section class="q-pt-none">
            <referenced-q-tree :nodes="nodes" />
          </q-card-section>
        </q-card>
      </q-expansion-item>
    </q-list>
    <referenced-q-tree v-else :nodes="nodes" />
  </template>
</template>

<style scoped lang="sass">
a
  color: #42b983
  cursor: pointer
  text-decoration: none
</style>
