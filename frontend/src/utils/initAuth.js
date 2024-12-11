import { useAuthStore } from '../stores/auth'

export default async function initAuth() {
  const authStore = useAuthStore()
  await authStore.checkAuth()
}