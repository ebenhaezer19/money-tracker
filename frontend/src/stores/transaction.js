import { defineStore } from 'pinia'

// Data dummy untuk testing
const DUMMY_CATEGORIES = [
  { id_category: '1', title: 'Makanan' },
  { id_category: '2', title: 'Transport' },
  { id_category: '3', title: 'Belanja' }
]

const DUMMY_TRANSACTIONS = [
  {
    id_transaction: '1',
    id_category: '1',
    amount: 50000,
    description: 'Makan siang',
    timestamp: '2024-03-20',
    isOverBudget: false
  },
  {
    id_transaction: '2',
    id_category: '2',
    amount: 200000,
    description: 'Bensin',
    timestamp: '2024-03-19',
    isOverBudget: true
  }
]

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: [],
    categories: []
  }),
  
  actions: {
    async fetchTransactions(filters = {}) {
      // Simulasi delay
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Filter data dummy
      let filtered = [...DUMMY_TRANSACTIONS]
      
      if (filters.categoryId) {
        filtered = filtered.filter(t => t.id_category === filters.categoryId)
      }
      
      if (filters.dateBegin) {
        filtered = filtered.filter(t => t.timestamp >= filters.dateBegin)
      }
      
      if (filters.dateEnd) {
        filtered = filtered.filter(t => t.timestamp <= filters.dateEnd)
      }
      
      this.transactions = filtered
      return filtered
    },

    async addTransaction(transactionData) {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const newTransaction = {
        id_transaction: Date.now().toString(),
        ...transactionData,
        isOverBudget: Math.random() > 0.7
      }
      
      this.transactions.push(newTransaction)
      return newTransaction
    },

    async editTransaction(transactionId, updates) {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const index = this.transactions.findIndex(t => t.id_transaction === transactionId)
      if (index !== -1) {
        this.transactions[index] = {
          ...this.transactions[index],
          ...updates
        }
        return this.transactions[index]
      }
      throw new Error('Transaction not found')
    },

    async fetchCategories() {
      await new Promise(resolve => setTimeout(resolve, 300))
      this.categories = DUMMY_CATEGORIES
      return DUMMY_CATEGORIES
    },

    async editCategory(categoryId, updates) {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const index = this.categories.findIndex(c => c.id_category === categoryId)
      if (index !== -1) {
        this.categories[index] = {
          ...this.categories[index],
          ...updates
        }
        return this.categories[index]
      }
      throw new Error('Category not found')
    },

    async hideCategory(categoryId) {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const index = this.categories.findIndex(c => c.id_category === categoryId)
      if (index !== -1) {
        this.categories[index].hidden = true
      }
    }
  }
})