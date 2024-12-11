import { useAuthStore } from './auth'

export function initAuth() {
  const authStore = useAuthStore()
  authStore.checkAuth()
} 