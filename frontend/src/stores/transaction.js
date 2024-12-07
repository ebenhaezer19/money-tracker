import { defineStore } from 'pinia'
import axios from 'axios'

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: [],
    categories: []
  }),
  
  actions: {
    async fetchTransactions(filters = {}) {
      try {
        const response = await axios.get('/api/transactions', { params: filters })
        this.transactions = response.data
        return response.data
      } catch (error) {
        throw error
      }
    },

    async addTransaction(transactionData) {
      try {
        const response = await axios.post('/api/transactions', transactionData)
        this.transactions.push(response.data)
        return response.data
      } catch (error) {
        throw error
      }
    },

    async editTransaction(transactionId, updates) {
      try {
        const response = await axios.put(`/api/transactions/${transactionId}`, updates)
        const index = this.transactions.findIndex(t => t.id_transaction === transactionId)
        if (index !== -1) {
          this.transactions[index] = response.data
        }
        return response.data
      } catch (error) {
        throw error
      }
    },

    async fetchCategories() {
      try {
        const response = await axios.get('/api/categories')
        this.categories = response.data
        return response.data
      } catch (error) {
        throw error
      }
    },

    async editCategory(categoryId, updates) {
      try {
        const response = await axios.put(`/api/categories/${categoryId}`, updates)
        const index = this.categories.findIndex(c => c.id_category === categoryId)
        if (index !== -1) {
          this.categories[index] = response.data
        }
        return response.data
      } catch (error) {
        throw error
      }
    },

    async hideCategory(categoryId) {
      try {
        await axios.put(`/api/categories/${categoryId}/hide`)
        const index = this.categories.findIndex(c => c.id_category === categoryId)
        if (index !== -1) {
          this.categories[index].hidden = true
        }
      } catch (error) {
        throw error
      }
    }
  }
}) 