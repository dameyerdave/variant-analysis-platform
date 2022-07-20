<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import api from '../api'
import DynamicTable from '../components/DynamicTable.vue'
import SimpleAnnotationWidget from '../widgets/SimpleAnnotationWidget.vue'
import AnnotationEditorWidget from '../widgets/AnnotationEditorWidget.vue'

const route = useRoute()
const store = useStore()

const { t } = useI18n()

const variant = ref(null)

const genes = computed(() => {
  const genes = []
  if (variant.value) {
    for (const transcript of variant.value.transcripts) {
      genes.push(transcript.gene)
    }
  }
  return genes
})

const queryData = async () => {
  try {
    const params = new URLSearchParams({ expand: true })
    const result = await api.query(`/variants/${route.params.id}?${params}`)
    // We expect exactly one result
    if (result.count === 1) {
      variant.value = result.results[0]
    }
  } catch (err) {
    console.error(err)
  }
}

onMounted(async () => {
  queryData()
})
</script>

<template>
  <div v-if="variant" class="container">
    <div v-if="route.query.sample__id" class="row">
      <div class="col-12">
        <DynamicTable
          :title="t('title.sample')"
          :details="true"
          :endpoint="`/samples/${route.query.sample__id}`"
          :config="store.getters.config.sample"
          :options="store.getters.config.options"
        />
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <DynamicTable
          :title="t('title.variant')"
          :details="true"
          endpoint="/variants/"
          :data="variant"
          :config="store.getters.config.variant"
          :options="store.getters.config.options"
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
    <div class="row">
      <div class="col-12">
        <q-list class="q-ma-md expansion-list">
          <q-expansion-item
            dense
            expand-separator
            switch-toggle-side
            header-class="expansion-header"
            :label="t('title.genes')"
            :default-opened="true"
          >
            <DynamicTable
              container-class="q-ma-0"
              flat
              endpoint="/genes/"
              :data="genes"
              :config="store.getters.config.gene"
              :options="store.getters.config.options"
            >
              <template #details="{ props }">
                <SimpleAnnotationWidget
                  :annotations="props.row.annotations"
                  :config="store.getters.config.gene"
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
            :label="t('title.transcripts')"
            :default-opened="true"
          >
            <DynamicTable
              container-class="q-ma-0"
              flat
              endpoint="/transcripts/"
              :data="variant.transcripts"
              :config="store.getters.config.transcript"
              :options="store.getters.config.options"
            >
              <template #details="{ props }">
                <SimpleAnnotationWidget
                  :annotations="props.row.annotations"
                  :config="store.getters.config.gene"
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
            :label="t('title.evidences')"
            :default-opened="true"
          >
            <DynamicTable
              container-class="q-ma-0"
              flat
              :details="false"
              :endpoint="`/variantevidences/?variant__id=${variant.id}&expand=true`"
              :config="store.getters.config.evidence"
              :options="store.getters.config.options"
              :expand-cols="['evidence']"
              :ignore-cols="[
                'id',
                'created_at',
                'variant',
                'extra',
                'annotations',
                'custom_annotations',
                'summary',
              ]"
            >
              <template #details="{ props }">
                <div class="summary">
                  {{ props.row.summary }}
                </div>
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
              :endpoint="`/variants/${variant.id}/?only=custom_annotations`"
              field="custom_annotations"
              :config="store.getters.config.transcript.custom_annotations"
            />
          </q-expansion-item>
        </q-list>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VariantDetailView',
}
</script>

<style lang="sass" scoped>
.summary
  width: 100%
  white-space: pre-line
  text-align: left
</style>
