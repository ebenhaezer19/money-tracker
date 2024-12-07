import { defineStore } from 'pinia'
// Hapus import axios karena tidak digunakan untuk sementara
// import axios from 'axios'

// Hardcoded credentials untuk testing
const VALID_CREDENTIALS = {
  username: 'admin',
  password: 'admin123'
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false
  }),
  
  actions: {
    async login(username, password) {
      // Simulasi API call
      await new Promise(resolve => setTimeout(resolve, 500))

      // Validasi sederhana
      if (username === VALID_CREDENTIALS.username && 
          password === VALID_CREDENTIALS.password) {
        const userData = {
          id_user: '1',
          username: username,
          role: 'admin'
        }
        this.user = userData
        this.isAuthenticated = true
        localStorage.setItem('user', JSON.stringify(userData))
        return userData
      } else {
        throw new Error('Username atau password salah')
      }
    },

    async logout() {
      // Simulasi API call
      await new Promise(resolve => setTimeout(resolve, 300))
      
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('user')
    },

    checkAuth() {
      const userData = localStorage.getItem('user')
      if (userData) {
        this.user = JSON.parse(userData)
        this.isAuthenticated = true
      }
    }
  }
}) 