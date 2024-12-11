<template>
  <div class="workspace-container">
    <!-- Top Bar with Filters -->
    <div class="top-bar">
      <div class="date-range">
        <input 
          type="date" 
          v-model="startDate" 
          @change="fetchTransactions"
          class="date-input"
        >
        <span class="date-separator">-</span>
        <input 
          type="date" 
          v-model="endDate" 
          @change="fetchTransactions"
          class="date-input"
        >
      </div>

      <!-- Category Checkboxes -->
      <div class="categories-filter">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-item"
          :style="{
            borderLeft: `4px solid ${category.color}`
          }"
        >
          <input 
            type="checkbox" 
            :id="category.id"
            v-model="category.isVisible"
            @change="updateVisibleCategories"
          >
          <label :for="category.id">{{ category.name }}</label>
        </div>
      </div>
    </div>

    <!-- Simple Table -->
    <div class="table-container">
      <div class="category-grid">
        <div v-for="category in visibleCategories" :key="category.id" class="category-row">
          <!-- Category Header -->
          <div 
            class="category-header"
            :style="{ borderLeft: `4px solid ${category.color}` }"
          >
            <strong>{{ category.name }}</strong>
            <button 
              @click="openAddTransaction(category.id)" 
              class="add-btn"
              :style="{ backgroundColor: category.color }"
            >
              + Add
            </button>
          </div>
          
          <!-- Transaction Grid -->
          <div class="transaction-grid">
            <!-- Header Columns -->
            <div class="grid-headers">
              <div class="grid-header">Date</div>
              <div class="grid-header">Amount</div>
              <div class="grid-header">Description</div>
            </div>
            
            <!-- Transaction Columns -->
            <div class="grid-columns">
              <!-- Date Column -->
              <div class="grid-column">
                <div 
                  v-for="transaction in getTransactionsByCategory(category.id)" 
                  :key="transaction.id"
                  class="transaction-seat"
                  :style="{ borderColor: category.color }"
                  @click="togglePopup(transaction.id)"
                >
                  {{ formatDate(transaction.date) }}
                </div>
              </div>

              <!-- Amount Column -->
              <div class="grid-column">
                <div 
                  v-for="transaction in getTransactionsByCategory(category.id)" 
                  :key="transaction.id"
                  class="transaction-seat"
                  :style="{ borderColor: category.color }"
                  @click="togglePopup(transaction.id)"
                >
                  IDR {{ formatNumber(transaction.amount) }}
                </div>
              </div>

              <!-- Description Column -->
              <div class="grid-column">
                <div 
                  v-for="transaction in getTransactionsByCategory(category.id)" 
                  :key="transaction.id"
                  class="transaction-seat"
                  :style="{ borderColor: category.color }"
                  @click="togglePopup(transaction.id)"
                >
                  {{ transaction.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction Form Modal -->
    <div v-if="showAddForm" class="modal-overlay">
      <div class="modal-content">
        <h2>{{ editingTransaction ? 'Edit Transaction' : 'Add Transaction' }}</h2>
        <form @submit.prevent="saveTransaction">
          <div class="form-group">
            <label>Date</label>
            <input type="date" v-model="formData.date" required>
          </div>

          <div class="form-group">
            <label>Amount (IDR)</label>
            <input 
              type="number" 
              v-model="formData.amount"
              placeholder="0"
              required
            >
          </div>

          <div class="form-group">
            <label>Category</label>
            <select v-model="formData.category" required>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="formData.description"
              rows="3"
              placeholder="Add description..."
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="cancelTransaction" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="save-btn">
              {{ editingTransaction ? 'Save' : 'Add' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useTransactionStore } from '../stores/transaction'

export default {
  name: 'MainWorkspace',
  data() {
    return {
      startDate: '',
      endDate: '',
      showAddForm: false,
      editingTransaction: null,
      formData: {
        date: '',
        amount: '',
        description: '',
        category: ''
      },
      categories: [
        { 
          id: 'cat1', 
          name: 'Category 1', 
          isVisible: true,
          budget: 1000000,
          color: '#4CAF50'  // Green
        },
        { 
          id: 'cat2', 
          name: 'Category 2', 
          isVisible: true,
          budget: 2000000,
          color: '#2196F3'  // Blue
        },
        { 
          id: 'cat3', 
          name: 'Category 3', 
          isVisible: true,
          budget: 1500000,
          color: '#FFC107'  // Amber
        },
        { 
          id: 'cat4', 
          name: 'Category 4', 
          isVisible: true,
          budget: 3000000,
          color: '#9C27B0'  // Purple
        }
      ],
      selectedTransaction: null,
      mockTransactions: [
        {
          id: 1,
          date: '2024-03-01',
          amount: 1500000,
          description: 'Gaji Bulanan',
          category: 'cat1'
        },
        {
          id: 2,
          date: '2024-03-02',
          amount: 500000,
          description: 'Belanja Bulanan',
          category: 'cat1'
        },
        {
          id: 3,
          date: '2024-03-03',
          amount: 250000,
          description: 'Makan di Restoran',
          category: 'cat2'
        },
        {
          id: 4,
          date: '2024-03-04',
          amount: 100000,
          description: 'Transportasi',
          category: 'cat2'
        },
        {
          id: 5,
          date: '2024-03-05',
          amount: 300000,
          description: 'Tagihan Internet',
          category: 'cat3'
        },
        {
          id: 6,
          date: '2024-03-06',
          amount: 200000,
          description: 'Tagihan Listrik',
          category: 'cat3'
        },
        {
          id: 7,
          date: '2024-03-07',
          amount: 1000000,
          description: 'Investasi Saham',
          category: 'cat4'
        },
        {
          id: 8,
          date: '2024-03-08',
          amount: 750000,
          description: 'Tabungan',
          category: 'cat4'
        }
      ]
    }
  },
  computed: {
    visibleCategories() {
      return this.categories.filter(cat => cat.isVisible)
    },
    transactions() {
      return this.mockTransactions
    }
  },
  methods: {
    formatNumber(value) {
      return value?.toLocaleString('id-ID') || '0'
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('id-ID')
    },
    getTransactionsByCategory(categoryId) {
      return this.transactions.filter(t => t.category === categoryId)
    },
    getTotalByCategory(categoryId) {
      return this.getTransactionsByCategory(categoryId)
        .reduce((sum, t) => sum + (Number(t.amount) || 0), 0)
    },
    isOverBudget(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      const total = this.getTotalByCategory(categoryId)
      return total > category.budget
    },
    updateVisibleCategories() {
      localStorage.setItem('visibleCategories', JSON.stringify(this.categories))
    },
    openAddTransaction(categoryId) {
      this.formData.category = categoryId
      this.showAddForm = true
    },
    cancelTransaction() {
      if (confirm('Are you sure you want to cancel this transaction?')) {
        this.showAddForm = false
        this.resetForm()
      }
    },
    async fetchTransactions() {
      const transactionStore = useTransactionStore()
      await transactionStore.fetchTransactions({
        startDate: this.startDate,
        endDate: this.endDate
      })
    },
    async saveTransaction() {
      const transactionStore = useTransactionStore()
      try {
        if (this.editingTransaction) {
          await transactionStore.updateTransaction({
            ...this.formData,
            id: this.editingTransaction.id
          })
        } else {
          await transactionStore.addTransaction(this.formData)
        }
        this.showAddForm = false
        this.resetForm()
        await this.fetchTransactions()
      } catch (error) {
        console.error('Error saving transaction:', error)
      }
    },
    async deleteTransaction(id) {
      if (confirm('Apakah Anda yakin ingin menghapus transaksi ini?')) {
        const transactionStore = useTransactionStore()
        try {
          await transactionStore.deleteTransaction(id)
          await this.fetchTransactions()
        } catch (error) {
          console.error('Error deleting transaction:', error)
        }
      }
    },
    editTransaction(transaction) {
      this.editingTransaction = transaction
      this.formData = { ...transaction }
      this.showAddForm = true
    },
    resetForm() {
      this.formData = {
        date: '',
        amount: '',
        description: '',
        category: ''
      }
      this.editingTransaction = null
    },
    togglePopup(transactionId) {
      if (this.selectedTransaction === transactionId) {
        this.selectedTransaction = null;
      } else {
        this.selectedTransaction = transactionId;
      }
    },
    closePopup() {
      this.selectedTransaction = null;
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId);
      return category ? category.name : '';
    }
  },
  async created() {
    const savedColumns = localStorage.getItem('visibleColumns')
    if (savedColumns) {
      this.attributes = JSON.parse(savedColumns)
    }
    
    if (!this.startDate) {
      const today = new Date()
      const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
      this.startDate = firstDay.toISOString().split('T')[0]
      this.endDate = today.toISOString().split('T')[0]
    }
    
    await this.fetchTransactions()
  }
}
</script>

<style scoped>
.workspace-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.top-bar {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.attributes-filter {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.attribute-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.add-transaction-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-top: 1rem;
  overflow-x: auto;
}

.excel-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #ddd;
}

.excel-table th,
.excel-table td {
  padding: 0.75rem;
  border: 1px solid #ddd;
  text-align: left;
}

.excel-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  position: sticky;
  top: 0;
}

.category-header-row {
  background-color: #f9f9f9;
}

.category-header-row.over-budget {
  background-color: #ffebee;
}

.category-header-row td {
  padding: 0.5rem 0.75rem;
}

.budget-info {
  float: right;
  color: #666;
  font-size: 0.9rem;
}

.transaction-row {
  cursor: pointer;
}

.transaction-row:hover {
  background-color: #f5f5f5;
}

.empty-message {
  text-align: center;
  color: #666;
  padding: 1rem;
  font-style: italic;
}

.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.delete-btn:hover {
  opacity: 1;
  color: #ef5350;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.attributes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.cancel-btn {
  background: #f5f5f5;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .top-bar {
    flex-direction: column;
  }
  
  .date-range {
    width: 100%;
  }
  
  .attributes-filter {
    justify-content: flex-start;
  }
}

.categories-filter {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  padding-left: 1rem;
  border-radius: 4px;
  background: #f5f5f5;
  transition: all 0.3s ease;
}

.category-item:hover {
  transform: translateX(4px);
}

.category-row {
  background: #f9f9f9;
  transition: background-color 0.3s ease;
}

.transaction-row {
  cursor: pointer;
  transition: all 0.3s ease;
}

.transaction-row:hover {
  background: #f5f5f5;
  transform: translateX(4px);
}

.add-btn {
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  color: white;
  transition: opacity 0.3s ease;
}

.add-btn:hover {
  opacity: 0.9;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f5f5f5;
}

.transaction-table {
  width: 100%;
  border-collapse: collapse;
}

.transaction-table th,
.transaction-table td {
  padding: 0.75rem;
  text-align: left;
  border: 1px solid #ddd;
}

.transaction-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.category-row {
  background: #f9f9f9;
}

.category-row.over-budget {
  background: #ffebee;
}

.transaction-row:hover {
  background: #f5f5f5;
}

.cell-with-tooltip {
  position: relative;
}

.tooltip {
  visibility: hidden;
  position: absolute;
  bottom: -35px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  z-index: 100;
  opacity: 0;
  transition: opacity 0.2s, visibility 0.2s;
}

.tooltip::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 0 5px 5px 5px;
  border-style: solid;
  border-color: transparent transparent rgba(0, 0, 0, 0.8) transparent;
}

.cell-with-tooltip:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

/* Pastikan tooltip tidak terpotong di baris terakhir */
.transaction-table tr:last-child .tooltip {
  bottom: auto;
  top: -35px;
}

.transaction-table tr:last-child .tooltip::before {
  top: auto;
  bottom: -5px;
  border-width: 5px 5px 0 5px;
  border-color: rgba(0, 0, 0, 0.8) transparent transparent transparent;
}

.cell-with-popup {
  position: relative;
  cursor: pointer;
}

.popup-details {
  display: none;
  position: absolute;
  left: 0;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  width: 300px;
  margin-top: 10px;
}

.popup-details.show {
  display: block;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #ddd;
}

.close-popup {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 0 4px;
}

.popup-content {
  padding: 16px;
}

.detail-row {
  display: flex;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.detail-label {
  width: 80px;
  color: #666;
  font-weight: 500;
}

.detail-value {
  flex: 1;
}

.popup-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-top: 1px solid #ddd;
  border-radius: 0 0 8px 8px;
}

.edit-btn, .delete-btn-popup {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  flex: 1;
}

.edit-btn {
  background: #2196F3;
  color: white;
}

.delete-btn-popup {
  background: #f44336;
  color: white;
}

/* Animasi untuk popup */
.popup-details {
  transform-origin: top center;
  transition: all 0.2s ease;
  opacity: 0;
  transform: translateY(-10px);
}

.popup-details.show {
  opacity: 1;
  transform: translateY(0);
}

/* Overlay untuk menutup popup saat klik di luar */
.workspace-container {
  position: relative;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 999;
  display: none;
}

.popup-overlay.show {
  display: block;
}

.category-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.category-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.transaction-grid {
  padding: 1rem;
  background: white;
  border-radius: 8px;
}

.grid-headers {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.grid-header {
  font-weight: 600;
  text-align: center;
}

.grid-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.grid-column {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.transaction-seat {
  width: 120px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border: 2px solid;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  text-align: center;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.transaction-seat:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-columns {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .grid-headers {
    grid-template-columns: 1fr;
  }
  
  .transaction-seat {
    width: 100%;
  }
}
</style> 