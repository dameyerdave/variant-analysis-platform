<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { useI18n } from 'vue-i18n'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const { t } = useI18n()

const props = defineProps({
  value: {
    validator: value => value === undefined || value === null || typeof value === 'object',
    required: true,
  },
  config: {
    validator: value => value === undefined || value === null || typeof value === 'object',
    default: () => {
      return {}
    },
  },
  options: {
    type: Object,
    default: () => {
      return {
        na_string: 'N/A',
      }
    },
  },
})

const populationMafData = computed(() => {
  if (props.value) {
    const overallMaf = props.value.ac / props.value.an
    let populations = props.value.populations
    if (props.config && 'populations' in props.config) {
      populations = props.value.populations.filter(pop => props.config.populations.includes(pop.id))
    }
    const labels = ['all', ...populations.map(pop => pop.id)]
    const mafs = [overallMaf, ...populations.map(pop => pop.ac / pop.an)]
    return {
      labels: labels,
      datasets: [
        {
          label: 'maf',
          backgroundColor: 'red',
          data: mafs,
        },
      ],
    }
  } else {
    return null
  }
})

const ageDistributionData = computed(() => {
  if (props.value) {
    return {
      labels: props.value.age_distribution.het.bin_edges,
      datasets: [
        {
          label: 'het',
          backgroundColor: 'blue',
          data: props.value.age_distribution.het.bin_freq,
        },
        {
          label: 'hom',
          backgroundColor: 'green',
          data: props.value.age_distribution.hom.bin_freq,
        },
      ],
    }
  } else {
    return null
  }
})

const chartOptions = {
  responsive: false,
}
</script>

<template>
  <div v-if="props.value" class="container">
    <div class="row">
      <div class="col">{{ t('label.minor_allele_frequency') }}</div>
      <div class="col">{{ t('label.age_distribution') }}</div>
    </div>
    <div class="row">
      <div class="col">
        <Bar
          v-if="populationMafData"
          :chart-options="chartOptions"
          :chart-data="populationMafData"
          :width="200"
          :height="200"
        />
      </div>
      <div class="col">
        <Bar
          v-if="ageDistributionData"
          :chart-options="chartOptions"
          :chart-data="ageDistributionData"
          :width="200"
          :height="200"
        />
      </div>
    </div>
  </div>
  <div v-else class="container">
    <div class="row">
      <div class="col">{{ props.options.na_string }}</div>
    </div>
  </div>
</template>
