<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import DynamicTable from '../components/DynamicTable.vue'
import SimpleAnnotationWidget from '../widgets/SimpleAnnotationWidget.vue'
import AnnotationEditorWidget from '../widgets/AnnotationEditorWidget.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const { t } = useI18n()

const openDetails = row => {
  router.push({
    name: 'variant_details',
    params: {
      id: row.id,
    },
    query: {
      sample__id: route.params.id,
    },
  })
}
</script>

<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <DynamicTable
          v-if="route.query"
          title="sample"
          :details="true"
          :endpoint="`/samples/${route.params.id}`"
          :config="store.getters.config.sample"
          :options="store.getters.config.options"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <q-list class="q-ma-md expansion-list">
          <q-expansion-item
            dense
            expand-separator
            switch-toggle-side
            header-class="expansion-header"
            :label="t('title.variants')"
            :default-opened="true"
          >
            <DynamicTable
              container-class="q-ma-0"
              flat
              :endpoint="`/samplevariants/?sample__id=${route.params.id}&expand=t`"
              :config="store.getters.config.samplevariant"
              :options="store.getters.config.options"
              @open-details="openDetails"
            >
              <template #details="{ props }">
                <SimpleAnnotationWidget
                  :annotations="props.row.annotations"
                  :config="store.getters.config.samplevariant"
                  :options="store.getters.config.options"
                />
              </template>
            </DynamicTable>
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
              :endpoint="`/samples/${route.params.id}/?only=custom_annotations`"
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
  name: 'SampleDetailView',
}
</script>
