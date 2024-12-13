import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_URL = import.meta.env.VITE_API_URL

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: []
  }),

  actions: {
    async fetchTransactions({ startDate, endDate }) {
      try {
        const authStore = useAuthStore()
        console.log('Store: Fetching transactions...', { startDate, endDate })
        
        const response = await axios.get(`${API_URL}/api/transactions`, {
          params: { 
            date_begin: startDate,
            date_end: endDate
          },
          ...authStore.getAuthHeader
        })
        
        console.log('Store: Raw API Response:', response)
        
        let transactions = []
        
        if (response.data && typeof response.data === 'object') {
          if (Array.isArray(response.data)) {
            transactions = response.data
          } else if (Array.isArray(response.data.transactions)) {
            transactions = response.data.transactions
          } else if (Array.isArray(response.data.data)) {
            transactions = response.data.data
          } else if (typeof response.data === 'object') {
            transactions = Object.values(response.data)
          }
        }
        
        console.log('Store: Extracted transactions:', transactions)
        
        transactions = transactions.filter(t => {
          const isValid = t && t.id && t.category && t.amount && t.date
          if (!isValid) {
            console.warn('Invalid transaction found:', t)
          }
          return isValid
        })
        
        const sortedData = transactions.sort((a, b) => new Date(b.date) - new Date(a.date))
        this.transactions = sortedData
        
        return sortedData
      } catch (error) {
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          authStore.logout()
        }
        throw error
      }
    },

    async addTransaction(transactionData) {
      try {
        const authStore = useAuthStore()
        console.log('Store: Adding transaction:', transactionData)
        
        const response = await axios.post(
          `${API_URL}/api/transactions`, 
          transactionData,
          authStore.getAuthHeader
        )
        
        console.log('Store: Add response:', response)
        
        let newTransaction = response.data
        if (response.data && response.data.transaction) {
          newTransaction = response.data.transaction
        }
        
        if (!newTransaction || !newTransaction.id) {
          throw new Error('Invalid transaction data received from server')
        }
        
        this.transactions = [newTransaction, ...this.transactions]
        
        return newTransaction
      } catch (error) {
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          authStore.logout()
        }
        throw error
      }
    },

    async updateTransaction(id, transactionData) {
      try {
        const response = await axios.put(
          `${API_URL}/api/transactions/${id}`, 
          transactionData,
          this.getAuthConfig() // Tambahkan header auth
        )
        const index = this.transactions.findIndex(t => t.id === id)
        if (index !== -1) {
          this.transactions[index] = response.data
        }
        return response.data
      } catch (error) {
        if (error.response?.status === 401) {
          window.location.href = '/login'
        }
        console.error('Error updating transaction:', error)
        throw error
      }
    },

    async deleteTransaction(id) {
      try {
        await axios.delete(
          `${API_URL}/api/transactions/${id}`,
          this.getAuthConfig() // Tambahkan header auth
        )
        this.transactions = this.transactions.filter(t => t.id !== id)
      } catch (error) {
        if (error.response?.status === 401) {
          window.location.href = '/login'
        }
        console.error('Error deleting transaction:', error)
        throw error
      }
    }
  }
})