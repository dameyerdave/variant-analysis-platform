<script setup>
import { defineProps } from 'vue'
import { ellipsis } from '../utils'

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
      }
    },
  },
})
</script>

<template>
  <div v-if="props.annotations" class="row">
    <div
      v-for="[key, value] in Object.entries(props.annotations)"
      :key="key"
      class="col-lg-3 col-md-6 col-xs-12"
    >
      <div class="row">
        <div class="col-6 text-right q-pr-xs">
          <b>{{ key }}:</b>
        </div>
        <div class="col-6 text-left">{{ ellipsis(value, 50, props.options.na_string) }}</div>
      </div>
    </div>
  </div>
  <div v-else>No annotations found</div>
</template>

<script>
export default {
  name: 'AnnotationWidget',
}
</script>
