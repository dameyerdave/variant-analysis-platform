<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import DynamicTable from '../components/DynamicTable.vue'
import SimpleAnnotationWidget from '../widgets/SimpleAnnotationWidget.vue'

const route = useRoute()
const store = useStore()
const { t } = useI18n()

const endpoint = computed(() => {
  if (route.params.id) {
    return `/genes/${route.params.id}`
  } else if (route.query) {
    const params = new URLSearchParams(route.query)
    return `/genes/?${params}`
  }
  return '/genes/'
})
</script>

<template>
  <div class="container">
    <div class="row">
      <div class="col">
        <DynamicTable
          :title="t('title.genes')"
          :endpoint="endpoint"
          :config="store.getters.config.gene"
          :options="store.getters.config.options"
        >
          <template #details="{ props }">
            <SimpleAnnotationWidget :annotations="props.row.annotations" />
          </template>
        </DynamicTable>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GeneView',
}
</script>
