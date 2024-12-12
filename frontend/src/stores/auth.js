import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    authStatus: false
  }),

  getters: {
    isAuthenticated: (state) => state.authStatus && !!state.user
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/auth/login`, {
          username,
          password
        })
        
        if (response.status === 200) {
          this.user = response.data.user
          this.authStatus = true
          
          // Simpan di localStorage
          localStorage.setItem('user', JSON.stringify(response.data.user))
          localStorage.setItem('isAuthenticated', 'true')
          
          return response.data
        }
      } catch (error) {
        console.error('Login error:', error)
        throw new Error(error.response?.data?.message || 'Login gagal')
      }
    },

    logout() {
      this.user = null
      this.authStatus = false
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
    },

    initAuth() {
      const user = localStorage.getItem('user')
      const isAuthenticated = localStorage.getItem('isAuthenticated')
      
      if (user && isAuthenticated) {
        this.user = JSON.parse(user)
        this.authStatus = true
      }
    }
  }
}) 