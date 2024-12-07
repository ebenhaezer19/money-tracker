import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import MainWorkspace from '@/views/MainWorkspace.vue'
import TransactionForm from '@/views/TransactionForm.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/',
    redirect: '/workspace'
  },
  {
    path: '/workspace',
    name: 'Workspace',
    component: MainWorkspace,
    meta: { requiresAuth: true }
  },
  {
    path: '/transaction/new',
    name: 'NewTransaction',
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
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)

  // Redirect ke login jika belum auth dan mencoba akses halaman yang butuh auth
  if (authRequired && !authStore.isAuthenticated) {
    return next('/login')
  }

  // Redirect ke workspace jika sudah auth dan mencoba akses login
  if (to.path === '/login' && authStore.isAuthenticated) {
    return next('/workspace')
  }

  next()
})

export default router