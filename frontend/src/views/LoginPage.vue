<template>
  <div class="login-container">
    <div class="login-card">
      <img class="logo-login" alt="Money Tracker Logo" src="https://moneytracker.domcloud.dev/logo2.svg">
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username"
            v-model="username"
            :disabled="isLoading"
            required
            autocomplete="username"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <div class="password-input">
            <input 
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              :disabled="isLoading"
              required
              autocomplete="current-password"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <button 
          type="submit" 
          class="login-button" 
          :disabled="isLoading || !isValid"
        >
          {{ isLoading ? 'Loading...' : 'Login' }}
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="login-help">
          <p>Demo credentials:</p>
          <p>Username: aaaaaa</p>
          <p>Password: aaaaaa</p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      username: '',
      password: '',
      error: '',
      isLoading: false,
      showPassword: false
    }
  },
  computed: {
    isValid() {
      return this.username.length > 0 && this.password.length > 0
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true
      this.error = ''
      
      try {
        const authStore = useAuthStore()
        await authStore.login(this.username, this.password)
        
        this.router.push('/workspace')
      } catch (err) {
        this.error = err.message
      } finally {
        this.isLoading = false
      }
    }
  },
  async created() {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      this.router.push('/workspace')
    }
  }
}
</script>

<style scoped>
.logo-login {
  display: block;
  margin: 0 auto 1rem;
  width: 50%;
}

.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  
  margin: 0;
  background-image: url("https://moneytracker.domcloud.dev/bg.svg");
  background-size: cover; /* Make the image cover the entire background */
  background-repeat: no-repeat; /* Prevent tiling */
  background-position: center; /* Center the image */
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.login-button {
  background-color: #4CAF50;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: red;
  text-align: center;
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.login-help {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
  color: #666;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.login-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>