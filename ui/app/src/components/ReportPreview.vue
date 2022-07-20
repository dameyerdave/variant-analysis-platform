<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const htmlContent = ref('')
const loading = ref(true)
const reportContainer = ref(null)

const getReport = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/report/base64')
    htmlContent.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const getPdf = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/report/pdf', { responseType: 'blob' })

    const fileURL = window.URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))

    // Open the pdf in a new browser tab
    window.open(fileURL, '_blank')
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

watch(htmlContent, content => {
  if (content) {
    reportContainer.value.data = `data:text/html;base64,${content}`
  }
})

onMounted(() => {
  getReport()
})
</script>

<template>
  <div class="full-width">
    <q-toolbar>
      <q-btn class="q-mr-xs" round size="sm" color="primary" icon="refresh" @click="getReport" />
      <q-btn class="q-mr-xs" round size="sm" color="primary" icon="picture_as_pdf" @click="getPdf" />
    </q-toolbar>
    <q-spinner-puff v-if="loading" color="primary" size="2em" />
    <object v-show="!loading" ref="reportContainer" class="full-width full-height" type="text/html" />
  </div>
</template>
