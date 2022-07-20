<script setup>
import { defineProps, computed } from 'vue'
import { useI18n } from 'vue-i18n'

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

const frequencies = computed(() => {
  let ret = {}
  if (Object.keys(props.value).length === 1) {
    ret = Object.values(props.value)[0]
  } else if (Object.keys(props.value).length > 1) {
    console.warn('Multiple entries in frequencies!', props.value)
  }
  return Object.entries(ret)
    .sort((a, b) => b[1] - a[1])
    .reduce(
      (_sorted, [k, v]) => ({
        ..._sorted,
        [k]: v,
      }),
      {}
    )
})
</script>

<template>
  <q-list v-if="frequencies">
    <q-expansion-item dense expand-separator class="no-border">
      <template #header>
        <q-item-section>
          {{ frequencies.gnomad }}
        </q-item-section>
      </template>
      <q-card>
        <q-card-section>
          <table>
            <tr>
              <th>{{ t('label.population') }}</th>
              <th>{{ t('label.maf') }}</th>
            </tr>
            <template v-for="(maf, population) in frequencies" :key="population">
              <tr v-if="maf > 0">
                <td>{{ population }}</td>
                <td>{{ maf }}</td>
              </tr>
            </template>
          </table>
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
  name: 'FrequenciesAnnotation',
}
</script>

<style scoped lang="sass">
table
  border-collapse: collapse
  border: 1px solid #bbb
  td, th
    text-align: left
    padding: 2px
    border: 1px solid #bbb
.q-card__section--vert
  padding: 0px
</style>
