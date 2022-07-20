<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import DynamicTable from '../components/DynamicTable.vue'
import AnnotationWidget from '../widgets/AnnotationWidget.vue'
import AnnotationEditorWidget from '../widgets/AnnotationEditorWidget.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const { t } = useI18n()

const endpoint = computed(() => {
  if (route.params.id) {
    return `/variants/${route.params.id}`
  } else if (route.query) {
    const params = new URLSearchParams(route.query)
    return `/variants/?${params}`
  }
  return '/variants/'
})

const openDetails = row => {
  router.push({
    name: 'transcripts',
    query: {
      variant__id: row.id,
      variant__sample__id: route.query.sample_variants__sample__id,
    },
  })
}
</script>

<template>
  <div class="container">
    <div v-if="route.query.sample_variants__sample__id" class="row">
      <div class="col-12">
        <DynamicTable
          v-if="route.query"
          title="sample"
          :details="true"
          :endpoint="`/samples/${route.query.sample_variants__sample__id}`"
          :config="store.getters.config.sample"
          :options="store.getters.config.options"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <DynamicTable
          title="Variants"
          :endpoint="endpoint"
          :config="store.getters.config.variant"
          :options="store.getters.config.options"
          @open-details="openDetails"
        >
          <template #details="{ props }">
            <AnnotationWidget :annotations="props.row.annotations" />
          </template>
        </DynamicTable>
      </div>
    </div>
    <hr />
    <div class="row">
      <div class="col-12">
        <q-list class="q-ma-md expansion-list">
          <q-expansion-item
            dense
            expand-separator
            switch-toggle-side
            header-class="expansion-header"
            :label="t('title.annotations')"
            :default-opened="true"
          >
            <AnnotationEditorWidget
              :endpoint="`/samples/${route.query.sample_variants__sample__id}/`"
              field="annotations"
              :readonly="true"
            />
          </q-expansion-item>
          <q-expansion-item
            dense
            expand-separator
            switch-toggle-side
            header-class="expansion-header"
            :label="t('title.custom_annotations')"
            :default-opened="true"
          >
            <AnnotationEditorWidget
              :endpoint="`/samples/${route.query.sample_variants__sample__id}/`"
              field="custom_annotations"
              :config="store.getters.config.sample.custom_annotations"
            />
          </q-expansion-item>
        </q-list>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SampleVariantView',
}
</script>
