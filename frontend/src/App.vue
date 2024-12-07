<template>
  <div class="app-container">
    <!-- Navbar will only show when user is logged in -->
    <nav v-if="isLoggedIn" class="navbar">
      <div class="nav-brand">
        <h1>Money Tracker</h1>
      </div>
      <div class="nav-links">
        <button @click="handleLogout" class="logout-btn">Logout</button>
      </div>
    </nav>

    <main :class="{ 'with-navbar': isLoggedIn }">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      const authStore = useAuthStore()
      return authStore.isAuthenticated
    }
  },
  methods: {
    handleLogout() {
      const authStore = useAuthStore()
      authStore.logout()
      this.$router.push('/login')
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

.app-container {
  min-height: 100vh;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
}

.nav-brand h1 {
  color: #4CAF50;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  align-items: center;
}

.logout-btn {
  background-color: #ff5252;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #ff1744;
}

main {
  padding: 1rem;
}

main.with-navbar {
  padding-top: 5rem;
}

@media (max-width: 768px) {
  .navbar {
    padding: 1rem;
  }
}
</style>