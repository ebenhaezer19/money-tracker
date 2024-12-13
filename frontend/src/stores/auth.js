import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    authStatus: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    getToken: (state) => state.token,
    getAuthHeader() {
      return {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      }
    }
  },

  actions: {
    async login(username, password) {
      try {
        const response = await axios.post(`${API_URL}/api/auth/login`, {
          username,
          password
        })
        
        if (response.data.token) {
          this.setAuth(response.data)
          return response.data
        }
        throw new Error('No token received')
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },

    setAuth(data) {
      this.token = data.token
      this.user = data.user
      this.authStatus = true
      
      // Simpan di localStorage
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      // Set token di axios default headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${data.token}`
    },

    clearAuth() {
      this.token = null
      this.user = null
      this.authStatus = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Hapus token dari axios headers
      delete axios.defaults.headers.common['Authorization']
    },

    logout() {
      this.clearAuth()
      window.location.href = '/login'
    },

    initAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        this.setAuth({
          token,
          user: JSON.parse(user)
        })
        return true
      }
      return false
    }
  }
}) 