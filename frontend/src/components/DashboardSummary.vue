<template>
  <div class="dashboard-summary">
    <div class="summary-cards">
      <div class="card total-spending">
        <h3>Total Pengeluaran</h3>
        <p class="amount">Rp {{ formatNumber(totalSpending) }}</p>
      </div>
      
      <div class="card budget-status">
        <h3>Status Budget</h3>
        <div class="budget-bars">
          <div v-for="cat in categories" :key="cat.id" class="budget-bar">
            <div class="bar-label">
              <span>{{ cat.name }}</span>
              <span>{{ (getUsagePercent(cat.id) * 100).toFixed(0) }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress" 
                :style="{
                  width: `${getUsagePercent(cat.id) * 100}%`,
                  backgroundColor: cat.color
                }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useCategoryStore } from '../stores/category'
import { useTransactionStore } from '../stores/transaction'

export default {
  name: 'DashboardSummary',
  computed: {
    categories() {
      return useCategoryStore().categories
    },
    totalSpending() {
      const transactionStore = useTransactionStore()
      return transactionStore.transactions.reduce((sum, t) => sum + t.amount, 0)
    }
  },
  methods: {
    formatNumber(value) {
      return new Intl.NumberFormat('id-ID').format(value)
    },
    getUsagePercent(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      const transactions = useTransactionStore().transactions
      const spent = transactions
        .filter(t => t.category === categoryId)
        .reduce((sum, t) => sum + t.amount, 0)
      return Math.min(spent / category.budget, 1)
    }
  }
}
</script>

<style scoped>
.dashboard-summary {
  margin-bottom: 2rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.amount {
  font-size: 2rem;
  font-weight: 600;
  color: #2196F3;
  margin-top: 0.5rem;
}

.budget-bars {
  margin-top: 1rem;
}

.budget-bar {
  margin-bottom: 1rem;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  transition: width 0.3s ease;
}
</style> 