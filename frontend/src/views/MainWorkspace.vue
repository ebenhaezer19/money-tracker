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
      <!-- Category Headers -->
      <div class="category-headers">
        <div class="category-row">
          <div 
            v-for="category in visibleCategories" 
            :key="category.id" 
            class="category-header-item"
            :class="{ 'over-budget': isOverBudget(category.id) }"
            :style="{
              borderTop: `4px solid ${category.color}`,
              background: `linear-gradient(to bottom, ${category.color}0A, white)`
            }"
          >
            <!-- Category Header dengan Total -->
            <div class="category-title" :style="{ borderBottom: `1px solid ${category.color}20` }">
              <div class="category-info">
                <h3 :style="{ color: category.color }">{{ category.name }}</h3>
                <p class="total-amount" :style="{ color: isOverBudget(category.id) ? '#ef4444' : category.color }">
                  Total: Rp {{ formatNumber(getTotalByCategory(category.id)) }}
                </p>
              </div>
              <button 
                @click="openAddTransaction(category.id)" 
                class="add-btn"
                :style="{ 
                  background: `linear-gradient(45deg, ${category.color}, ${adjustColor(category.color, -20)})`,
                  boxShadow: `0 4px 15px ${category.color}40`
                }"
              >
                +
              </button>
            </div>

            <!-- Transaction List -->
            <div class="transaction-list">
              <div 
                v-for="transaction in getTransactionsByCategory(category.id)" 
                :key="transaction.id"
                class="transaction-item"
                @click="togglePopup(transaction.id)"
                @mousedown="startPress(transaction)"
                @mouseup="cancelPress"
                @mouseleave="cancelPress"
                @touchstart.prevent="startPress(transaction)"
                @touchend.prevent="cancelPress"
                @touchcancel="cancelPress"
              >
                <div class="transaction-amount">Rp {{ formatNumber(transaction.amount) }}</div>
                <div class="transaction-date">{{ formatDate(transaction.date) }}</div>
                <div class="transaction-description">{{ transaction.description }}</div>
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

    <!-- Tambahkan popup card di bawah table-container, sebelum transaction form modal -->
    <div v-if="selectedTransaction" class="transaction-card-popup">
      <div class="card-content">
        <div class="card-header">
          <h3>Transaction Details</h3>
          <button class="close-card" @click="closePopup">×</button>
        </div>
        
        <div class="card-body">
          <div class="transaction-info">
            <div class="info-row">
              <div class="info-icon">📅</div>
              <div class="info-content">
                <div class="info-label">Date</div>
                <div class="info-value">{{ formatDate(getSelectedTransaction.date) }}</div>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-icon">💰</div>
              <div class="info-content">
                <div class="info-label">Amount</div>
                <div class="info-value amount">IDR {{ formatNumber(getSelectedTransaction.amount) }}</div>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-icon">📝</div>
              <div class="info-content">
                <div class="info-label">Description</div>
                <div class="info-value">{{ getSelectedTransaction.description }}</div>
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <button class="edit-action" @click="editTransaction(getSelectedTransaction)">
              ✏️ Edit
            </button>
            <button class="delete-action" @click="deleteTransaction(getSelectedTransaction.id)">
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useTransactionStore } from '../stores/transaction'
import { useCategoryStore } from '../stores/category'

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
      pressTimer: null,
      pressedTransaction: null,
      selectedTransaction: null,
      mockTransactions: [
        {
          id: 1,
          category: 'cat1',
          date: '2024-03-15',
          amount: 500000,
          description: 'Belanja bulanan'
        },
        {
          id: 2,
          category: 'cat1',
          date: '2024-03-16',
          amount: 750000,
          description: 'Pembayaran listrik'
        },
        {
          id: 3,
          category: 'cat2',
          date: '2024-03-17',
          amount: 1200000,
          description: 'Biaya sekolah'
        },
        {
          id: 4,
          category: 'cat3',
          date: '2024-03-18',
          amount: 300000,
          description: 'Makan malam'
        },
        {
          id: 5,
          category: 'cat2',
          date: '2024-03-19',
          amount: 2500000,
          description: 'Pembayaran kursus'
        },
        {
          id: 6,
          category: 'cat4',
          date: '2024-03-20',
          amount: 1500000,
          description: 'Service mobil'
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
    },
    getSelectedTransaction() {
      return this.transactions.find(t => t.id === this.selectedTransaction) || {}
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
          await transactionStore.updateTransaction(
            this.editingTransaction.id,
            this.formData
          )
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
      const transaction = this.mockTransactions.find(t => t.id === transactionId)
      this.selectedTransaction = transaction
    },
    closePopup() {
      this.selectedTransaction = null;
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId);
      return category ? category.name : '';
    },
    startPress(transaction) {
      this.pressTimer = setTimeout(() => {
        this.showDeleteConfirmation(transaction);
      }, 800); // 800ms untuk long press
      this.pressedTransaction = transaction;
    },
    cancelPress() {
      if (this.pressTimer) {
        clearTimeout(this.pressTimer);
        this.pressTimer = null;
      }
      this.pressedTransaction = null;
    },
    showDeleteConfirmation(transaction) {
      if (confirm(`Apakah Anda yakin ingin menghapus transaksi ini?\n\nDetail:\nTanggal: ${this.formatDate(transaction.date)}\nJumlah: IDR ${this.formatNumber(transaction.amount)}\nDeskripsi: ${transaction.description}`)) {
        this.deleteTransaction(transaction.id);
      }
    },
    adjustColor(hex, percent) {
      // Convert hex to RGB
      let r = parseInt(hex.substring(1,3), 16);
      let g = parseInt(hex.substring(3,5), 16);
      let b = parseInt(hex.substring(5,7), 16);

      // Adjust color
      r = Math.max(0, Math.min(255, r + percent));
      g = Math.max(0, Math.min(255, g + percent));
      b = Math.max(0, Math.min(255, b + percent));

      // Convert back to hex
      return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
    }
  },
  async created() {
    const transactionStore = useTransactionStore()
    const categoryStore = useCategoryStore()
    
    try {
      // Fetch categories
      await categoryStore.fetchCategories()
      
      // Set default dates if not set
      if (!this.startDate || !this.endDate) {
        const today = new Date()
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
        this.startDate = firstDay.toISOString().split('T')[0]
        this.endDate = today.toISOString().split('T')[0]
      }
      
      // Fetch transactions
      await transactionStore.fetchTransactions({
        startDate: this.startDate,
        endDate: this.endDate
      })
    } catch (error) {
      console.error('Error initializing workspace:', error)
    }
  }
}
</script>

<style scoped>
.workspace-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.date-input {
  padding: 0.6rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #2d3748;
  transition: all 0.2s ease;
}

.date-input:focus {
  border-color: #2196F3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
  outline: none;
}

.date-separator {
  color: #64748b;
  font-weight: 500;
}

.categories-filter {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
  flex: 1;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.2s ease;
  cursor: pointer;
}

.category-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.category-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  cursor: pointer;
}

.category-item label {
  font-size: 0.95rem;
  color: #2d3748;
  font-weight: 500;
  cursor: pointer;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .top-bar {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .date-range {
    width: 100%;
    justify-content: space-between;
  }
  
  .categories-filter {
    width: 100%;
    justify-content: flex-start;
  }
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-top: 1rem;
  width: 100%;
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
  user-select: none; /* Mencegah seleksi teks saat long press */
  touch-action: none; /* Mencegah gesture default di mobile */
}

.transaction-seat:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.transaction-seat.pressed {
  transform: scale(0.95);
  opacity: 0.8;
  background-color: #f5f5f5;
}

@keyframes pressAnimation {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0.95);
  }
}

.popup-modal {
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

.popup-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  min-width: 300px;
  max-width: 400px;
}

.transaction-details {
  margin: 1rem 0;
}

.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.edit-btn, .close-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.edit-btn {
  background: #2196F3;
  color: white;
}

.close-btn {
  background: #f5f5f5;
}

.transaction-seat {
  padding: 0.5rem;
  border: 2px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  margin: 0.25rem;
  display: inline-block;
}

.transaction-seat:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

.transaction-card-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.card-content {
  background: white;
  width: 90%;
  max-width: 400px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

.card-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.close-card {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-card:hover {
  background: #f5f5f5;
}

.card-body {
  padding: 20px;
}

.transaction-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-row {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.info-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 12px;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  font-size: 1.1rem;
  color: #333;
}

.info-value.amount {
  font-weight: 600;
  color: #2196F3;
}

.card-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.edit-action,
.delete-action {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.edit-action {
  background: #e3f2fd;
  color: #1976D2;
}

.delete-action {
  background: #ffebee;
  color: #d32f2f;
}

.edit-action:hover {
  background: #bbdefb;
}

.delete-action:hover {
  background: #ffcdd2;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.category-headers {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
  width: 100%;
}

.category-row {
  display: contents;
}

.category-header-item {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  overflow: hidden;
  min-height: 300px;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.category-header-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.category-title {
  padding: 1.5rem;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(8px);
  position: relative;
}

.category-info {
  padding-right: 3rem;
}

.add-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: none;
  color: white;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(45deg, #2196F3, #1976D2);
  box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.add-btn:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
}

.total-amount {
  margin: 0.7rem 0 0;
  font-size: 1.2rem;
  color: #2c3e50;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.total-amount::before {
  content: '💰';
  font-size: 1.1rem;
}

.transaction-list {
  flex: 1;
  padding: 1.2rem;
  overflow-y: auto;
  background: rgba(248, 249, 250, 0.5);
}

.transaction-item {
  padding: 1rem 1.2rem;
  border-radius: 12px;
  background: white;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.transaction-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-left: 4px solid #2196F3;
}

.transaction-amount {
  font-size: 1.15rem;
  font-weight: 600;
  color: #1976D2;
  margin-bottom: 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.transaction-date {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.transaction-date::before {
  content: '📅';
  font-size: 0.9rem;
}

.transaction-description {
  font-size: 0.95rem;
  color: #475569;
  line-height: 1.4;
}

/* Custom scrollbar untuk transaction list */
.transaction-list::-webkit-scrollbar {
  width: 6px;
}

.transaction-list::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.02);
  border-radius: 3px;
}

.transaction-list::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.1);
  border-radius: 3px;
}

.transaction-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0,0,0,0.2);
}

/* Style untuk kategori yang over budget */
.category-header-item.over-budget {
  background: linear-gradient(to bottom right, #fff5f5, #fff) !important;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.over-budget .total-amount {
  color: #ef4444 !important;
}

.over-budget .total-amount::before {
  content: '⚠️';
}
</style> 