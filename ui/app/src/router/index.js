import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/change_password',
    name: 'change_password',
    component: () => import('../views/ChangePasswordView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('../views/SearchView.vue'),
  },
  {
    path: '/samples',
    name: 'samples',
    component: () => import('../views/SampleView.vue'),
  },
  {
    path: '/samples/:id',
    name: 'sample_details',
    component: () => import('../views/SampleDetailView.vue'),
  },
  {
    path: '/samples/:sample_id/variant/:variant_id',
    name: 'sample_variants',
    component: () => import('../views/SampleVariantView.vue'),
  },
  {
    path: '/variants',
    name: 'variants',
    component: () => import('../views/VariantView.vue'),
  },
  {
    path: '/variants/:id',
    name: 'variant_details',
    component: () => import('../views/VariantDetailView.vue'),
  },
  {
    path: '/genes/:id?',
    name: 'genes',
    component: () => import('../views/GeneView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (!['login', 'register'].includes(to.name)) {
    // If we do not want to login or register we check
    // the jwt token exists, if not we route to the login
    // page
    if (!store.getters.jwt) {
      next({
        path: '/login',
        query: { next: to.fullPath },
      })
    } else if (Object.keys(store.getters.config).length === 0) {
      // If there is not config loaded, we load it
      store
        .dispatch('loadConfig')
        .then(() => next())
        .catch(err => console.error(err))
    } else {
      next()
    }
  } else {
    if (store.getters.jwt) {
      // It make no sense to login or register if we
      // are already logged in so we route back to the
      // path we come from
      console.debug('from, to', from, to)
      next({
        path: from.path,
      })
    } else {
      next()
    }
  }
})

export default router
