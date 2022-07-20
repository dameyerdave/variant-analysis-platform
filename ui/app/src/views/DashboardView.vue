<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const statistics = ref(null)
const { t } = useI18n()

const getStatistics = async () => {
  try {
    const { data } = await axios.get('/statistics/')
    statistics.value = data
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  getStatistics()
})
</script>

<template>
  <div v-if="statistics" class="q-pa-md row items-start q-gutter-md">
    <q-card>
      <q-card-section>
        {{ t('label.num_samples') }}
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-h6">
          {{ statistics.counts.samples }}
        </div>
      </q-card-section>
    </q-card>

    <q-card>
      <q-card-section>
        {{ t('label.num_variants') }}
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-h6">
          {{ statistics.counts.variants }}
        </div>
      </q-card-section>
    </q-card>

    <q-card>
      <q-card-section>
        {{ t('label.num_transcripts') }}
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-h6">
          {{ statistics.counts.transcripts }}
        </div>
      </q-card-section>
    </q-card>

    <q-card>
      <q-card-section>
        {{ t('label.num_genes') }}
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-h6">
          {{ statistics.counts.genes }}
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>
