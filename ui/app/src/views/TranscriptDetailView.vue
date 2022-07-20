<script setup>
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import AnnotationsEditorWidget from '../widgets/AnnotationEditorWidget.vue'
import DynamicTable from '../components/DynamicTable.vue'

const route = useRoute()
const store = useStore()

const { t } = useI18n()

const endpoint = `/transcripts/${route.params.id}/`
</script>

<template>
  <div class="container">
    <div class="row">
      <div class="col">
        <DynamicTable
          :title="t('title.transcript')"
          :details="true"
          :endpoint="endpoint"
          :config="store.getters.config.transcript"
          :options="store.getters.config.options"
        />
      </div>
    </div>
    <div class="row">
      <div class="col q-px-md">
        <AnnotationsEditorWidget
          :title="t('title.annotations')"
          :endpoint="endpoint"
          field="annotations"
          :readonly="true"
        />
      </div>
    </div>
    <hr />
    <div class="row">
      <div class="col q-px-md">
        <AnnotationsEditorWidget
          :title="t('title.custom_annotations')"
          :endpoint="endpoint"
          field="custom_annotations"
          :config="store.getters.config.transcript.custom_annotations"
        />
      </div>
    </div>
  </div>
</template>
