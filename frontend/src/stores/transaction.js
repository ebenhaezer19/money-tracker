import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const API_URL = import.meta.env.VITE_API_URL

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: []
  }),

  actions: {
    // Helper untuk mendapatkan config axios dengan auth header
    getAxiosConfig(params = {}) {
      const authStore = useAuthStore()
      const token = authStore.getToken
      
      return {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true,
        ...params
      }
    },

    async fetchTransactions({ startDate, endDate }) {
      try {
        console.log('Store: Fetching transactions...', { startDate, endDate })
        
        const response = await axios.get(`${API_URL}/api/transactions`, 
          this.getAxiosConfig({
            params: { 
              date_begin: startDate,
              date_end: endDate
            }
          })
        )
        
        console.log('Store: Raw API Response:', response)
        
        let transactions = []
        if (response.data && typeof response.data === 'object') {
          if (Array.isArray(response.data)) {
            transactions = response.data
          } else if (Array.isArray(response.data.transactions)) {
            transactions = response.data.transactions
          } else if (Array.isArray(response.data.data)) {
            transactions = response.data.data
          }
        }
        
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
        console.log('Store: Adding transaction:', transactionData)
        
        const response = await axios.post(
          `${API_URL}/api/transactions`, 
          transactionData,
          this.getAxiosConfig()
        )
        
        console.log('Store: Add response:', response)
        
        let newTransaction = null
        if (response.data) {
          if (response.data.transaction) {
            newTransaction = response.data.transaction
          } else if (response.data.id) {
            newTransaction = response.data
          }
        }

        if (!newTransaction || !newTransaction.id) {
          console.error('Invalid response structure:', response.data)
          throw new Error('Invalid transaction data received from server')
        }
        
        this.transactions = [newTransaction, ...this.transactions]
        return newTransaction
      } catch (error) {
        console.error('Store: Error adding transaction:', error)
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          authStore.logout()
        }
        throw error
      }
    },

    async updateTransaction(id, transactionData) {
      try {
        console.log('Store: Updating transaction:', { id, data: transactionData })
        
        const response = await axios.put(
          `${API_URL}/api/transactions/${id}`, 
          transactionData,
          this.getAxiosConfig()
        )
        
        console.log('Store: Update response:', response)
        
        const updatedTransaction = response.data
        const index = this.transactions.findIndex(t => t.id === id)
        if (index !== -1) {
          this.transactions[index] = updatedTransaction
          this.transactions.sort((a, b) => new Date(b.date) - new Date(a.date))
        }
        
        return updatedTransaction
      } catch (error) {
        console.error('Store: Error updating transaction:', error)
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          authStore.logout()
        }
        throw error
      }
    },

    async deleteTransaction(id) {
      try {
        console.log('Store: Deleting transaction:', id)
        
        await axios.delete(
          `${API_URL}/api/transactions/${id}`,
          this.getAxiosConfig()
        )
        
        this.transactions = this.transactions.filter(t => t.id !== id)
        console.log('Store: Transaction deleted successfully')
      } catch (error) {
        console.error('Store: Error deleting transaction:', error)
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          authStore.logout()
        }
        throw error
      }
    }
  }
})