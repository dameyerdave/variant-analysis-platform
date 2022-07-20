<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useQuasar } from 'quasar'

const store = useStore()
const router = useRouter()
const { t } = useI18n()
const $q = useQuasar()

const password = ref(null)
const new_password = ref(null)
const new_password_again = ref(null)

const change_password = async () => {
  try {
    await axios.post('/auth/users/change_password/', {
      password: password.value,
      new_password: new_password.value,
    })
    $q.notify({
      type: 'positive',
      message: t('message.successfully_changed_password'),
    })
    store.dispatch('removeToken')
    router.push({
      path: '/login',
    })
  } catch (err) {
    console.error(err)
  }
}
</script>

<template>
  <div class="row justify-center">
    <div class="q-pa-md col-4">
      <q-card class="q-pa-sm">
        <q-form class="q-gutter-md" @submit="change_password">
          <input value="xxx" type="hidden" autocomplete="current-username" />

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
            v-model="new_password"
            filled
            type="password"
            :label="t('label.new_password')"
            :hint="t('hint.new_password')"
            autocomplete="new-password"
            lazy-rules
            :rules="[val => (val && val.length > 0) || t('value_error.password')]"
          />

          <q-input
            v-model="new_password_again"
            filled
            type="password"
            :label="t('label.new_password_again')"
            :hint="t('hint.new_password_again')"
            autocomplete="new-password"
            lazy-rules
            :rules="[
              val => (val && val.length > 0) || t('value_error.password'),
              val => (val && val.length > 0 && val === new_password) || t('value_error.passwords_not_equal'),
              val => (val && val.length > 0 && val !== password) || t('value_error.password_same_as_old'),
            ]"
          />

          <div class="row justify-end">
            <q-btn :label="t('label.change')" type="submit" color="primary" />
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
