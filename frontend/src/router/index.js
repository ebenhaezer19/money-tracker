import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginPage from '../views/LoginPage.vue'
import MainWorkspace from '../views/MainWorkspace.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)

  if (authRequired && !authStore.isAuthenticated) {
    return next('/login')
  }

  if (to.path === '/login' && authStore.isAuthenticated) {
    return next('/workspace')
  }

  next()
})

export default router