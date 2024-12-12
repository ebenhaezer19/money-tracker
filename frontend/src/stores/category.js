import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchCategories() {
      this.loading = true
      try {
        const response = await axios.get('/api/categories')
        this.categories = response.data.map(cat => ({
          ...cat,
          isVisible: true
        }))
      } catch (error) {
        console.error('Error fetching categories:', error)
        this.error = error.response?.data?.message || 'Error fetching categories'
      } finally {
        this.loading = false
      }
    }
  }
}) 