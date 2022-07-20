<script setup>
import { defineProps, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { openURL } from 'quasar'

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

const summary = computed(() => {
  if (props.value === undefined || props.value === null) return null
  const items = {}
  for (const item of props.value) {
    if (!(item.clinical_significance in items)) {
      items[item.clinical_significance] = {
        count: 0,
        conditions: new Set(),
        details: [],
      }
    }
    items[item.clinical_significance].count += 1
    const details = {
      review_status: item.review_status,
      last_evaluated: item.last_evaluated,
      submitter_name: item.submitter_name,
      conditions: new Set(),
    }
    for (const condition of item.conditions) {
      const cond = `${condition.name} (${condition.medgen_id})`
      details.conditions.add(cond)
      items[item.clinical_significance].conditions.add(condition)
    }
    items[item.clinical_significance].details.push(details)
  }
  return items
})

const color_lookup = {
  'Pathogenic': 'red-5',
  'Likely pathogenic': 'orange-5',
  'pathologic': 'red-5',
  'not provided': 'blue-5',
  'Uncertain significance': 'blue-5',
  'no known pathogenicity': 'blue-5',
  'Benign': 'green-5',
  'Likely benign': 'light-green-5',
}
</script>

<template>
  <q-list v-if="summary">
    <q-expansion-item
      v-for="(item, clinsig) in summary"
      :key="clinsig"
      dense
      expand-separator
      class="no-border"
    >
      <template #header>
        <q-item-section>
          <q-badge :color="color_lookup[clinsig]" class="q-ml-xs">
            {{ clinsig }} ({{ item.count }})
            <q-tooltip class="bg-grey" :offset="[10, 10]">
              <table>
                <tr>
                  <th>{{ t('label.condition') }}</th>
                  <th>{{ t('label.last_evaluated') }}</th>
                  <th>{{ t('label.review_status') }}</th>
                  <th>{{ t('label.submitter_name') }}</th>
                </tr>

                <tr></tr>
                <tr v-for="(details, idx) in item.details" :key="'details' + idx">
                  <td>{{ [...details.conditions].join(', ') }}</td>
                  <td>{{ details.last_evaluated }}</td>
                  <td>{{ details.review_status }}</td>
                  <td>{{ details.submitter_name }}</td>
                </tr>
              </table>
            </q-tooltip>
          </q-badge>
        </q-item-section>
      </template>
      <q-card>
        <q-card-section>
          <ul>
            <li v-for="condition in item.conditions" :key="condition">
              {{ condition.name }}
              <a @click="openURL(`https://www.ncbi.nlm.nih.gov/medgen/${condition.medgen_id}`)">
                ({{ condition.medgen_id }})
              </a>
            </li>
          </ul>
        </q-card-section>
      </q-card>
    </q-expansion-item>
  </q-list>
  <template v-else>
    {{ props.options.na_string }}
  </template>
</template>

<script>
export default {
  name: 'ClinvarSubmissions',
}
</script>

<style scoped lang="sass">
a
  color: #42b983
  cursor: pointer
  text-decoration: none
ul
  margin-block-start: 2px
  margin-block-end: 2px
  margin-right: 5px
  li
    text-align: left
table
  border-collapse: collapse
  td, th
    text-align: left
    padding: 2px
    border: 1px solid #4c4c4c
.q-card__section--vert
  padding: 0px
</style>
