import { useAuthStore } from '../stores/auth'

export default async function initAuth() {
  const authStore = useAuthStore()
  return await authStore.checkAuth()
}