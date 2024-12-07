import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import MainWorkspace from '@/views/MainWorkspace.vue'
import TransactionForm from '@/views/TransactionForm.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/workspace',
    name: 'Workspace',
    component: MainWorkspace,
    meta: { requiresAuth: true }
  },
  {
    path: '/transaction',
    name: 'Transaction',
    component: TransactionForm,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard untuk autentikasi
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/')
  } else if (to.path === '/' && isAuthenticated) {
    next('/workspace')
  } else {
    next()
  }
})

export default router