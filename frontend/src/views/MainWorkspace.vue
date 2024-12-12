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
      <table class="transaction-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Date</th>
            <th>Amount (IDR)</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="category in visibleCategories" :key="category.id">
            <!-- Category Row with Add Button -->
            <tr 
              class="category-row" 
              :class="{ 'over-budget': isOverBudget(category.id) }"
              :style="{
                borderLeft: `4px solid ${category.color}`
              }"
            >
              <td colspan="5">
                <div class="category-header">
                  <strong>{{ category.name }}</strong>
                  <button 
                    @click="openAddTransaction(category.id)" 
                    class="add-btn"
                    :style="{
                      backgroundColor: category.color
                    }"
                    title="Add new transaction"
                  >
                    + Add Transaction
                  </button>
                </div>
              </td>
            </tr>
            <!-- Transaction Rows -->
            <tr 
              v-for="transaction in getTransactionsByCategory(category.id)" 
              :key="transaction.id"
              @dblclick="editTransaction(transaction)"
              class="transaction-row"
              :style="{
                borderLeft: `4px solid ${category.color}`
              }"
            >
              <td></td>
              <td>
                <div 
                  class="transaction-seat"
                  :class="{ 'pressed': pressedTransaction?.id === transaction.id }"
                  :style="{ borderColor: category.color }"
                  @click="togglePopup(transaction.id)"
                  @mousedown="startPress(transaction)"
                  @mouseup="cancelPress"
                  @mouseleave="cancelPress"
                  @touchstart.prevent="startPress(transaction)"
                  @touchend.prevent="cancelPress"
                  @touchcancel="cancelPress"
                >
                  {{ formatDate(transaction.date) }}
                </div>
              </td>
              <td>
                <div 
                  class="transaction-seat"
                  :class="{ 'pressed': pressedTransaction?.id === transaction.id }"
                  :style="{ borderColor: category.color }"
                  @click="togglePopup(transaction.id)"
                  @mousedown="startPress(transaction)"
                  @mouseup="cancelPress"
                  @mouseleave="cancelPress"
                  @touchstart.prevent="startPress(transaction)"
                  @touchend.prevent="cancelPress"
                  @touchcancel="cancelPress"
                >
                  IDR {{ formatNumber(transaction.amount) }}
                </div>
              </td>
              <td>
                <div 
                  class="transaction-seat"
                  :class="{ 'pressed': pressedTransaction?.id === transaction.id }"
                  :style="{ borderColor: category.color }"
                  @click="togglePopup(transaction.id)"
                  @mousedown="startPress(transaction)"
                  @mouseup="cancelPress"
                  @mouseleave="cancelPress"
                  @touchstart.prevent="startPress(transaction)"
                  @touchend.prevent="cancelPress"
                  @touchcancel="cancelPress"
                >
                  {{ transaction.description }}
                </div>
              </td>
              <td>
                <button @click.stop="deleteTransaction(transaction.id)" class="delete-btn">
                  🗑️
                </button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
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

    <!-- Tambahkan popup modal untuk detail transaksi -->
    <div v-if="selectedTransaction" class="popup-modal" @click.self="closePopup">
      <div class="popup-content">
        <h3>Detail Transaksi</h3>
        <div class="transaction-details">
          <p><strong>Tanggal:</strong> {{ formatDate(selectedTransaction.date) }}</p>
          <p><strong>Jumlah:</strong> IDR {{ formatNumber(selectedTransaction.amount) }}</p>
          <p><strong>Deskripsi:</strong> {{ selectedTransaction.description }}</p>
        </div>
        <div class="popup-actions">
          <button @click="editTransaction(selectedTransaction)" class="edit-btn">Edit</button>
          <button @click="closePopup" class="close-btn">Tutup</button>
        </div>
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
    togglePopup(transactionId) {
      const transaction = this.mockTransactions.find(t => t.id === transactionId)
      this.selectedTransaction = transaction
    },
    
    closePopup() {
      this.selectedTransaction = null
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

.transaction-seat {
  user-select: none; /* Mencegah seleksi teks saat long press */
  touch-action: none; /* Mencegah gesture default di mobile */
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
</style> 