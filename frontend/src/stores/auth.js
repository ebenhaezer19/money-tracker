import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    authStatus: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/auth/login', {
          username,
          password
        })
        
        if (response.data.token) {
          this.token = response.data.token
          this.user = response.data.user
          this.authStatus = true
          
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          localStorage.setItem('isAuthenticated', 'true')
          
          return response.data
        }
        throw new Error('No token received')
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.authStatus = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
    },

    initAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
        this.authStatus = true
      }
    }
  }
}) 