import { defineStore } from 'pinia'
import axios from 'axios'

// Data dummy yang lebih lengkap
const DUMMY_TRANSACTIONS = [
  {
    id: 1,
    date: '2024-01-15',
    amount: 150000,
    category: 'Food',
    payment: 'Cash',
    status: 'Completed',
    type: 'Expense',
    description: 'Lunch'
  },
  {
    id: 2,
    date: '2024-01-20',
    amount: 500000,
    category: 'Transport',
    payment: 'Transfer',
    status: 'Completed',
    type: 'Expense',
    description: 'Gas & parking'
  },
  {
    id: 3,
    date: '2024-02-01',
    amount: 2500000,
    category: 'Salary',
    payment: 'Transfer',
    status: 'Completed',
    type: 'Income',
    description: 'January salary'
  }
]

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: []
  }),

  actions: {
    async fetchTransactions({ startDate, endDate }) {
      // Filter berdasarkan tanggal
      this.transactions = DUMMY_TRANSACTIONS.filter(transaction => {
        const transactionDate = new Date(transaction.date)
        const start = startDate ? new Date(startDate) : null
        const end = endDate ? new Date(endDate) : null

        if (start && end) {
          return transactionDate >= start && transactionDate <= end
        } else if (start) {
          return transactionDate >= start
        } else if (end) {
          return transactionDate <= end
        }
        return true
      })
    },

    async addTransaction(transaction) {
      const newTransaction = {
        id: Date.now(),
        ...transaction,
        date: transaction.date || new Date().toISOString().split('T')[0]
      }
      this.transactions.unshift(newTransaction) // Menambahkan di awal array
    },

    async updateTransaction(transaction) {
      const index = this.transactions.findIndex(t => t.id === transaction.id)
      if (index !== -1) {
        this.transactions[index] = {
          ...transaction,
          date: transaction.date || new Date().toISOString().split('T')[0]
        }
      }
    },

    async deleteTransaction(id) {
      this.transactions = this.transactions.filter(t => t.id !== id)
    }
  }
})