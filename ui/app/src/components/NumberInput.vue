<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  modelValue: { type: Number, required: true },
})

const emit = defineEmits(['update:model-value'])

const update = value => {
  console.log('update', value)
  emit('update:model-value', Number(value))
}
</script>

<template>
  <QInput :model-value="props.modelValue" type="number" @update:model-value="update" />
</template>
