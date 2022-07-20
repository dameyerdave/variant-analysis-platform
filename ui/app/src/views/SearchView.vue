<script setup>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DynamicTable from '../components/DynamicTable.vue'

const store = useStore()
const router = useRouter()
const { t } = useI18n()

const openVariantDetails = row => {
  router.push({ name: 'transcripts', query: { variant__id: row.id } })
}
</script>

<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <q-input
          v-model="query"
          filled
          type="search"
          :hint="t('hint.search')"
          :rules="[val => !!val || t('error.search_value_is_required')]"
          @keyup.enter.prevent="search"
        >
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
    </div>
    <div v-if="bump" class="row">
      <div class="col-12">
        <DynamicTable
          :key="'variant' + bump"
          :title="t('title.variants')"
          :endpoint="`/variants/?search=${query}`"
          :config="store.getters.config.variant"
          :options="store.getters.config.options"
          @open-details="openVariantDetails"
        />
      </div>
    </div>
    <div v-if="bump" class="row">
      <div class="col-12">
        <DynamicTable
          :key="'transcript' + bump"
          :title="t('title.transcripts')"
          :endpoint="`/transcripts/?search=${query}`"
          :config="store.getters.config.transcript"
          :options="store.getters.config.options"
        />
      </div>
    </div>
    <div v-if="bump" class="row">
      <div class="col-12">
        <DynamicTable
          :key="'gene' + bump"
          :title="t('title.genes')"
          :details="true"
          :endpoint="`/genes/?search=${query}`"
          :config="store.getters.config.gene"
          :options="store.getters.config.options"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      query: '',
      variants: [],
      transcripts: [],
      genes: [],
      loading: true,
      bump: 0,
    }
  },
  methods: {
    async search() {
      if (this.query) {
        this.bump++
      }
    },
  },
}
</script>
