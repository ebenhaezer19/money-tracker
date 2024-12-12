import { defineStore } from 'pinia'
import axios from '../utils/axios'  // Import custom axios instance

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchTransactions({ startDate, endDate }) {
      this.loading = true
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        const response = await axios.get('/api/transactions', {
          data: {
            user_id: user.id,
            date_begin: startDate,
            date_end: endDate
          }
        })
        this.transactions = response.data
      } catch (error) {
        console.error('Error fetching transactions:', error)
        this.error = error.response?.data?.message || 'Error fetching transactions'
      } finally {
        this.loading = false
      }
    },

    async addTransaction(transactionData) {
      try {
        const user = JSON.parse(localStorage.getItem('user'))
        const response = await axios.post('/api/transactions', {
          user_id: user.id,
          ...transactionData
        })
        return response.data
      } catch (error) {
        console.error('Error adding transaction:', error)
        throw error
      }
    }
  }
})