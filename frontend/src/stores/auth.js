import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false
  }),
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/auth/login', {
          username,
          password
        })
        this.user = response.data
        this.isAuthenticated = true
        localStorage.setItem('user', JSON.stringify(response.data))
        return response.data
      } catch (error) {
        throw error
      }
    },

    async logout() {
      try {
        await axios.post('/api/auth/logout', {
          userId: this.user?.id_user
        })
        this.user = null
        this.isAuthenticated = false
        localStorage.removeItem('user')
      } catch (error) {
        throw error
      }
    }
  }
}) 