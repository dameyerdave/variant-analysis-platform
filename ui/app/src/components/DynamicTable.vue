<script setup>
import _ from 'lodash'
import formatters from '../formatters'
import { useI18n } from 'vue-i18n'
import { useQuasar } from 'quasar'
import axios from 'axios'
import api from '../api'

import { defineProps, defineEmits, ref, computed, onMounted, useSlots } from 'vue'

const { t } = useI18n()
const q = useQuasar()
const slots = useSlots()

const props = defineProps({
  endpoint: { type: String, required: true },
  data: { type: [Array, Object], default: () => null },
  config: {
    type: Object,
    default: () => {
      return {}
    },
  },
  actions: {
    type: Object,
    default: () => {
      return {
        show: true,
        delete: true,
      }
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
  title: { type: String, default: undefined },
  noDataLabel: { type: String, default: 'No data available' },
  expandCols: { type: Array, default: () => [] },
  ignoreCols: { type: Array, default: () => [] },
  details: { type: Boolean, default: false },
  containerClass: { type: String, default: 'q-pa-md' },
  flat: { type: Boolean, default: false },
})

const emit = defineEmits(['open-details'])

const loading = ref(true)
const meta = ref([])
const data = ref({})
const pagination = ref({ rowsPerPage: 0 })

const columns = computed(() => {
  if (_.isArray(meta.value)) {
    let cols = meta.value.filter(
      m => props.ignoreCols.includes(m.key) === false && props.expandCols.includes(m.key) === false
    )
    cols = cols.map(c => ({
      name: c.key,
      field: c.key,
      label: _.upperFirst(c.ui.label).replaceAll('_', ' '),
      format: formatByType,
      sortable: true,
      align: 'left',
    }))
    // if we have a config for this component we use it
    if (props.config && props.config.fields) {
      const configured_cols = []
      for (const field of props.config.fields) {
        if (_.isString(field)) {
          const _col = cols.find(c => c.field === field)
          if (_col) {
            configured_cols.push(_col)
          }
        } else if (_.isObject(field)) {
          const _field = Object.keys(field)[0]
          const field_config = field[_field]
          let _col = cols.find(c => c.field === _field)
          // if we have sub field
          if (!_col && _field.includes('__')) {
            _col = {
              name: _field,
              field: _field,
              label: _.upperFirst(_field.split('__')[1]).replaceAll('_', ' '),
              format: formatByType,
              sortable: true,
              align: 'left',
            }
          }
          if (_col) {
            if (field_config) {
              if ('label' in field_config) {
                _col.label = _.upperFirst(field_config.label).replaceAll('_', ' ')
              }
              if ('format' in field_config) {
                _col.format = formatters[field_config.format]
              }
              _col.field_config = field_config
            }
            configured_cols.push(_col)
          }
        }
      }
      // we handle the flags
      if (props.config.flags) {
        configured_cols.push({
          name: 'flags',
          field: 'flags',
          label: t('label.flags'),
          align: 'left',
        })
      }
      return configured_cols
    } else {
      return cols
    }
  } else {
    return []
  }
})

const rows = computed(() => {
  let _data = []
  if (data.value) {
    if ('results' in data.value) {
      _data = data.value.results
    } else if (!_.isArray(data.value)) {
      _data = [data.value]
    } else {
      _data = data.value
    }
  }
  return _expandCols(_data)
})

const details_slot_present = computed(() => {
  // if the details slot has content
  return slots.details !== undefined
})

const openDetails = row => {
  emit('open-details', row)
}

const formatByType = val => {
  if (_.isString(val)) {
    return val
  } else if (_.isArray(val)) {
    return val.join(', ')
  } else if (_.isObject(val)) {
    let ret = ''
    for (const [k, v] of Object.entries(val)) {
      ret += `${k}: ${v} | `
    }
    // remove last separator
    return ret.substring(0, ret.length - 3)
  } else {
    return val
  }
}

const _expandCols = rows => {
  if (rows) {
    for (const col of props.expandCols) {
      for (const row of rows) {
        if (col in row) {
          // we found a row to expand
          if (_.isObject(row[col])) {
            for (const [k, v] of Object.entries(row[col])) {
              if (!meta.value.find(m => m.key === k)) {
                meta.value.push({ key: k, ui: { label: k } })
              }
              row[k] = v
            }
            delete row[col]
          }
        }
      }
    }
    if (columns.value) {
      for (const col of columns.value) {
        // Here we handle dot notation of additional values in json fields
        // to show in table
        for (const row of rows) {
          if (col.field.includes('__')) {
            const [_col, _key] = col.field.split('__')
            if (_col in row && row[_col]) {
              row[col.field] = row[_col][_key]
            } else {
              row[col.field] = props.options.na_string
            }
          }
        }
      }
    }
  }
  return rows
}

const queryData = async () => {
  loading.value = true
  data.value = null
  try {
    meta.value = await api.meta(props.endpoint)
    if (props.data) {
      data.value = props.data
    } else {
      data.value = await api.query(props.endpoint)
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const deleteRow = row => {
  q.dialog({
    dark: false,
    title: t('dialog.title.confirm_delete'),
    message: t('dialog.message.confirm_delete'),
    cancel: true,
    persistent: true,
    color: 'red-5',
    focus: 'cancel',
  }).onOk(async () => {
    try {
      await axios.delete(`${props.endpoint}${row.id}`)
      queryData()
    } catch (err) {
      console.error(err)
    }
  })
}

onMounted(async () => {
  queryData()
})
</script>

<template>
  <div :class="containerClass">
    <q-table
      v-model="pagination"
      dense
      :flat="flat"
      :title="title"
      :rows="rows"
      :columns="columns"
      :loading="loading"
      :no-data-label="noDataLabel"
      :hide-pagination="details"
      separator="cell"
      :class="details ? 'header-table' : 'sticky-header-table'"
      row-key="id"
      :pagination-label="(start, end, total) => `${start} - ${end} / ${total}`"
      :rows-per-page-options="[0]"
    >
      <template #header="props">
        <q-tr :props="props">
          <q-th v-if="details_slot_present" auto-width />
          <q-th v-for="col in props.cols" :key="col.name" :props="props">
            {{ col.label }}
          </q-th>
          <q-th v-if="!details" auto-width />
        </q-tr>
      </template>

      <template #body="props">
        <q-tr :props="props">
          <q-td v-if="details_slot_present" auto-width>
            <q-btn
              size="sm"
              color="accent"
              round
              dense
              :icon="props.expand ? 'remove' : 'add'"
              @click="props.expand = !props.expand"
            />
          </q-td>
          <q-td v-for="col in props.cols" :key="col.name" :props="props">
            <template v-if="col.value && 'field_config' in col && 'highlight' in col.field_config">
              <template v-for="val in col.value.split(',')">
                <q-badge
                  v-if="val.trim() in col.field_config.highlight"
                  :key="'highlight-' + val"
                  :color="col.field_config.highlight[val.trim()]"
                  class="q-ml-xs"
                >
                  {{ val }}
                </q-badge>
                <q-badge v-else :key="'non-highlight-' + val" color="blue-5" class="q-ml-xs">
                  {{ val }}
                </q-badge>
              </template>
            </template>
            <template
              v-else-if="
                col.value &&
                'field_config' in col &&
                'format' in col.field_config &&
                col.field_config.format == 'ellipsis'
              "
            >
              <span :title="props.row[col.name]"> {{ col.value }} </span>
            </template>
            <template v-else-if="col.name === 'flags'">
              <template v-for="(flag_config, flag) in config.flags">
                <q-icon v-if="props.row[`flag_${flag}`]" :key="flag" :name="flag_config.icon">
                  <q-tooltip
                    class="bg-blue-5 text-white shadow-4"
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    {{ flag }}
                  </q-tooltip>
                </q-icon>
              </template>
            </template>
            <template v-else>
              {{ col.value }}
            </template>
          </q-td>
          <q-td v-if="!details" auto-width>
            <q-btn
              v-if="actions.show"
              class="q-mr-xs"
              size="sm"
              color="blue-5"
              round
              dense
              icon="chevron_right"
              @click="openDetails(props.row)"
            />
            <q-btn
              v-if="actions.delete"
              size="sm"
              color="red-5"
              round
              dense
              icon="delete"
              @click="deleteRow(props.row)"
            />
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <slot name="details" :props="props" />
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  name: 'DynamicTable',
}
</script>

<style scoped lang="sass">
a
  color: #42b983

label
  margin: 0 0.5em
  font-weight: bold

code
  background-color: #eee
  padding: 2px 4px
  border-radius: 4px
  color: #304455
</style>
