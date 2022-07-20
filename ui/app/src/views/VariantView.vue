<script setup>
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import DynamicTable from '../components/DynamicTable.vue'
import SimpleAnnotationWidget from '../widgets/SimpleAnnotationWidget.vue'

const router = useRouter()
const store = useStore()

const openDetails = row => {
  router.push({ name: 'variant_details', params: { id: row.id } })
}
</script>

<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <DynamicTable
          title="Variants"
          endpoint="/variants/"
          :config="store.getters.config.variant"
          @open-details="openDetails"
        >
          <template #details="{ props }">
            <SimpleAnnotationWidget
              :annotations="props.row.annotations"
              :config="store.getters.config.variant"
              :options="store.getters.config.options"
            />
          </template>
        </DynamicTable>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VariantView',
}
</script>
