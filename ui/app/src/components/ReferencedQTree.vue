<script setup>
import { defineProps } from 'vue'
import { openURL } from 'quasar'

const props = defineProps({
  nodes: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <q-tree :nodes="props.nodes" node-key="key">
    <template #default-header="prop">
      <a v-if="prop.node.reference" @click="openURL(prop.node.reference)">
        {{ prop.node.label }}
      </a>
      <template v-else>
        {{ prop.node.label }}
      </template>
    </template>
  </q-tree>
</template>

<style scoped lang="sass">
a
  color: #42b983
  cursor: pointer
  text-decoration: none
</style>
