<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { useQuasar } from 'quasar'

const store = useStore()
const router = useRouter()
const { t } = useI18n()
const $q = useQuasar()

const email = ref(null)
const password = ref(null)
const token = ref(null)
const error = ref(false)

const login = async () => {
  error.value = false
  await store.dispatch('obtainToken', {
    email: email.value,
    password: password.value,
    token: token.value,
  })
  $q.notify({
    type: 'positive',
    message: t('message.successfully_logged_in'),
  })
  if (store.getters.jwt) {
    let searchParams = new URLSearchParams(window.location.search)

    if (searchParams.has('next')) {
      router.push({ path: `${searchParams.get('next')}` })
    } else {
      router.push({ path: '/' })
    }
  } else {
    error.value = true
  }
}
</script>

<template>
  <div class="row justify-center">
    <div class="q-pa-md col-4">
      <q-card v-if="error" class="bg-red-5 text-black text-bold q-mb-md">
        <q-card-section>
          {{ t('error.cannot_login') }}
        </q-card-section>
      </q-card>
      <q-card class="q-pa-sm">
        <q-form class="q-gutter-md" @submit="login">
          <q-input
            v-model="email"
            filled
            type="email"
            :label="t('label.email')"
            :hint="t('hint.email')"
            autocomplete="current-email"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.email')]"
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
            v-model="token"
            filled
            type="number"
            :label="t('label.token')"
            :hint="t('hint.token')"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.token')]"
          />

          <div class="row justify-end">
            <q-btn
              class="q-mr-md"
              :label="t('label.register')"
              color="secondary"
              @click="router.push({ path: '/register' })"
            />
            <q-btn :label="t('label.login')" type="submit" color="primary" />
          </div>
        </q-form>
      </q-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
}
</script>
