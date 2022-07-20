<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { onInactivity } from './utils'
import { useQuasar } from 'quasar'

const { locale, t } = useI18n()
const store = useStore()
const router = useRouter()
const $q = useQuasar()

const tab = ref('search')

const filter = computed({
  get: () => {
    return store.getters.filter
  },
  set: value => {
    store.dispatch('setFilter', value)
    // if the filter value changes we reload the page
    window.location.reload()
  },
})

const logout = () => {
  store.dispatch('removeToken')
  $q.notify({
    type: 'positive',
    message: t('message.logged_out'),
  })
  router.push({ path: '/login' })
}

const change_password = () => {
  router.push({ path: '/change_password' })
}

// If the user is inactive for x min we logout
onInactivity(import.meta.env.VITE_APP_INACTIVITY_TIMEOUT || 10, logout)
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-primary text-white" height-hint="98">
      <q-toolbar>
        <q-avatar>
          <img src="/logo.png" />
        </q-avatar>
        <q-toolbar-title align="left"> Variant Analysis Platform </q-toolbar-title>
        <q-select v-model="locale" :options="['en', 'de']" />
        <q-select v-model="filter" :options="['all', 'default']" />
        <q-btn-dropdown
          v-if="store.getters.jwt && store.getters.user"
          stretch
          flat
          :label="store.getters.user.first_name ? store.getters.user.first_name : store.getters.user.username"
        >
          <q-item v-close-popup clickable @click="change_password">
            <q-item-section>
              <q-item-label>{{ t('label.change_password') }}</q-item-label>
            </q-item-section>
          </q-item>
          <q-separator />
          <q-item v-close-popup clickable @click="logout">
            <q-item-section>
              <q-item-label>{{ t('label.logout') }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-btn-dropdown>
      </q-toolbar>

      <q-tabs v-model="tab" align="left">
        <q-route-tab to="/search" :label="t('nav.search')" />
        <q-route-tab to="/samples" :label="t('nav.samples')" />
        <q-route-tab to="/variants" :label="t('nav.variants')" />
        <q-route-tab to="/genes" :label="t('nav.genes')" />
      </q-tabs>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script></script>

<style lang="sass">
/* Global style definitions */
#app
  min-width: 100%
  min-height: 100%
  font-family: Avenir, Helvetica, Arial, sans-serif
  -webkit-font-smoothing: antialiased
  -moz-osx-font-smoothing: grayscale
  text-align: center
  color: #2c3e50

.header-table
  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    /* bg color is important for th; just specify one */
    background-color: #eee

.sticky-header-table
  /* height or max-height is important */
  max-height: calc(100vh - 140px)

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    /* bg color is important for th; just specify one */
    background-color: #eee

  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0

  /* this is when the loading indicator appears */
  &.q-table--loading thead tr:last-child th
    /* height of all previous header rows */
    top: 48px

.expansion-header
  background-color: rgb(220,220,220)
  border-bottom: 1px solid rgb(206,206,206)
  margin-top: 10px
  padding-top: 5px
  padding-bottom: 8px
  border-radius: 4px

  .q-item__label
    text-align: left
    font-size: 20px
    letter-spacing: 0.005em
    font-weight: 400

.expansion-list
  .q-expansion-item__container
    border-left: 1px solid rgb(240,240,240)
    border-right: 1px solid rgb(240,240,240)
    border-radius: 4px
    box-shadow: 0 1px 5px rgb(0 0 0 / 20%), 0 2px 2px rgb(0 0 0 / 14%), 0 3px 1px -2px rgb(0 0 0 / 12%)

.no-border .q-expansion-item__container
      border: 0px
      border-radius: unset
      box-shadow: unset
</style>
