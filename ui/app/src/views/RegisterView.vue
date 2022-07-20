<script setup>
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()

const password = ref(null)
const password2 = ref(null)
const first_name = ref(null)
const last_name = ref(null)
const email = ref(null)

const register = async () => {
  try {
    await axios.post('/auth/users/register/', {
      email: email.value,
      password: password.value,
      first_name: first_name.value,
      last_name: last_name.value,
    })
    router.push({ path: '/login' })
  } catch (err) {
    console.error(err)
  }
}
</script>

<template>
  <div class="row justify-center">
    <div class="q-pa-md col-4">
      <q-card class="q-pa-sm">
        <q-form class="q-gutter-md" @submit="register">
          <q-input
            v-model="email"
            filled
            type="email"
            :label="t('label.email')"
            :hint="t('hint.email')"
            autocomplete="current-email"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.last_name')]"
          />

          <q-input
            v-model="password"
            filled
            type="password"
            :label="t('label.password')"
            :hint="t('hint.password')"
            autocomplete="current-password"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.password')]"
          />

          <q-input
            v-model="password2"
            filled
            type="password"
            :label="t('label.password_again')"
            :hint="t('hint.password_again')"
            autocomplete="current-password"
            lazy-rules
            :rules="[
              val => (val && val.length > 0) || t('value_error.password'),
              val => (val && val.length > 0 && val === password) || t('value_error.passwords_not_equal'),
            ]"
          />

          <q-input
            v-model="first_name"
            filled
            :label="t('label.first_name')"
            :hint="t('hint.first_name')"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.first_name')]"
          />

          <q-input
            v-model="last_name"
            filled
            :label="t('label.last_name')"
            :hint="t('hint.last_name')"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.last_name')]"
          />

          <div class="row justify-end">
            <q-btn :label="t('label.register')" type="submit" color="primary" />
          </div>
        </q-form>
      </q-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterView',
}
</script>
