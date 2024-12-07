import { defineStore } from 'pinia'
import axios from 'axios'

// Demo credentials
const DEMO_USER = {
  username: 'admin',
  password: 'admin123',
  token: 'demo-token-123',
  userData: {
    id: 1,
    username: 'admin',
    role: 'admin'
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(username, password) {
      try {
        // Simulasi delay seperti API call sungguhan
        await new Promise(resolve => setTimeout(resolve, 500))

        // Cek dengan demo credentials
        if (username === DEMO_USER.username && password === DEMO_USER.password) {
          this.token = DEMO_USER.token
          this.user = DEMO_USER.userData
          
          localStorage.setItem('token', DEMO_USER.token)
          return { token: DEMO_USER.token, user: DEMO_USER.userData }
        }
        
        throw new Error('Username atau password salah')
        
        // Uncomment kode di bawah ini jika backend sudah siap
        /*
        const response = await axios.post('http://localhost:3000/api/auth/login', {
          username,
          password
        })
        
        const { token, user } = response.data
        this.token = token
        this.user = user
        
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return response.data
        */
      } catch (error) {
        throw new Error(error.message || 'Login gagal')
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },

    async checkAuth() {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          // Untuk demo, langsung set user jika token cocok
          if (token === DEMO_USER.token) {
            this.token = token
            this.user = DEMO_USER.userData
            return true
          }
          
          // Uncomment untuk verifikasi dengan backend nanti
          /*
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          const response = await axios.get('http://localhost:3000/api/auth/verify')
          this.user = response.data.user
          */
          
          return true
        } catch (error) {
          this.logout()
          return false
        }
      }
      return false
    }
  }
}) 