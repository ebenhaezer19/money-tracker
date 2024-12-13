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
    },

    async updateCategoryColor(categoryId, color) {
      try {
        const response = await axios.put(`/api/categories/${categoryId}`, {
          color: color
        })
        
        // Update local state
        const index = this.categories.findIndex(c => c.id === categoryId)
        if (index !== -1) {
          this.categories[index] = {
            ...this.categories[index],
            color: response.data.color
          }
        }
        
        return response.data
      } catch (error) {
        console.error('Error updating category color:', error)
        throw error
      }
    },

    async addCategory(categoryData) {
      try {
        const response = await axios.post('/api/categories', categoryData)
        
        // Format data sesuai dengan yang diharapkan
        const newCategory = {
          ...response.data,
          isVisible: true,
          id: response.data.id,  // Pastikan id ada
          name: response.data.name,  // Pastikan name ada
          color: response.data.color  // Pastikan color ada
        }
        
        // Update local state
        this.categories.push(newCategory)
        
        return newCategory
      } catch (error) {
        console.error('Error adding category:', error)
        throw error
      }
    }
  }
}) 