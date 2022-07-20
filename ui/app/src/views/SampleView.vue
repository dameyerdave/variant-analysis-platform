<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import DynamicTable from '../components/DynamicTable.vue'
import AnnotationWidget from '../widgets/AnnotationWidget.vue'
import ReportPreview from '../components/ReportPreview.vue'

const router = useRouter()
const store = useStore()

const openDetails = row => {
  router.push({ name: 'sample_details', params: { id: row.id } })
}
</script>

<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <DynamicTable
          title="Samples"
          :endpoint="`/samples/`"
          :config="store.getters.config.sample"
          @open-details="openDetails"
        >
          <template #details="{ props }">
            <AnnotationWidget :annotations="props.row.annotations" />
          </template>
        </DynamicTable>
      </div>
      <div class="col-12">
        <ReportPreview />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SampleView',
}
</script>
