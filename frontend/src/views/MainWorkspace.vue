<template>
  <div class="workspace-container">
    <!-- Statistics Section (Pindah ke atas) -->
    <div class="statistics-section">
      <!-- Total Overview -->
      <div class="stat-card total-overview">
        <h3>Total Pengeluaran</h3>
        <div class="total-amount-large">
          IDR {{ formatNumber(getTotalExpense) }}
        </div>
        <div class="stat-period">
          {{ formatDate(startDate) }} - {{ formatDate(endDate) }}
        </div>
      </div>
    </div>

    <!-- Top Bar with Filters (Pindah ke tengah) -->
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
            borderLeft: `4px solid ${category.color}`,
            background: `${category.color}10`
          }"
        >
          <input 
            type="checkbox" 
            :id="category.id"
            v-model="category.isVisible"
            @change="updateVisibleCategories"
          >
          <label 
            :for="category.id"
            style="color: #000000"
          >
            {{ category.name }}
          </label>
          <div class="color-picker">
            <input 
              type="color"
              :value="category.color"
              @change="updateCategoryColor(category.id, $event.target.value)"
              class="color-input"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Simple Table -->
    <div class="table-container">
      <!-- Category Headers -->
      <div class="category-headers">
        <!-- Tambahkan header actions di sini -->
        <div class="category-headers-actions">
          <button @click="showAddCategoryForm = true" class="add-category-btn">
            <span class="btn-icon">+</span>
            <span class="btn-text">Add Category</span>
          </button>
        </div>

        <div class="category-row">
          <div 
            v-for="category in visibleCategories" 
            :key="category.id" 
            class="category-header-item"
            :class="{ 'over-budget': isOverBudget(category.id) }"
            :style="{
              borderTop: `4px solid ${category.color}`,
              background: isOverBudget(category.id) 
                ? 'linear-gradient(to bottom, #fff5f5, #fee2e2)' 
                : `linear-gradient(to bottom, ${category.color}0A, white)`
            }"
          >
            <!-- Category Header dengan Total -->
            <div class="category-title" :style="{ borderBottom: `1px solid ${category.color}20` }">
              <div class="category-info">
                <div v-if="editingCategoryId === category.id" class="edit-category-name">
                  <input 
                    type="text"
                    v-model="editCategoryName"
                    @blur="saveCategoryName(category.id)"
                    @keyup.enter="saveCategoryName(category.id)"
                    @keyup.esc="cancelEditCategory"
                    ref="categoryNameInput"
                    class="edit-category-input"
                  >
                </div>
                <h3 
                  v-else
                  @click="startEditCategory(category)"
                  :style="{ color: category.color }"
                  class="category-name"
                >
                  {{ category.name }}
                </h3>
                <p class="total-amount" :style="{ 
                  color: isOverBudget(category.id) ? '#ef4444' : category.color 
                }">
                  Total: IDR {{ formatNumber(getTotalByCategory(category.id)) }}
                </p>
              </div>
              <div class="category-actions">
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
                <button 
                  @click.stop="confirmDeleteCategory(category.id)"
                  class="delete-category-btn"
                  :style="{
                    background: '#fff',
                    color: '#ef4444',
                    border: '2px solid #ef4444'
                  }"
                >
                  🗑️
                </button>
              </div>
            </div>

            <!-- Transaction List -->
            <div class="transaction-list">
              <div 
                v-for="transaction in getTransactionsByCategory(category.id)" 
                :key="transaction.id"
                class="transaction-item"
                @click="togglePopup(transaction.id)"
                :style="{
                  borderLeft: `4px solid ${category.color}`,
                  '&:hover': {
                    borderLeft: `6px solid ${category.color}`,
                    background: `${category.color}05`
                  }
                }"
              >
                <div class="transaction-amount">IDR {{ formatNumber(transaction.amount) }}</div>
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
              <div class="info-icon" 
                   :style="{ background: getCategoryColor(getSelectedTransaction.category) + '20' }">
                📂
              </div>
              <div class="info-content">
                <div class="info-label">Category</div>
                <div class="info-value category" 
                     :style="{ color: getCategoryColor(getSelectedTransaction.category) }">
                  {{ getCategoryName(getSelectedTransaction.category) }}
                </div>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-icon">💰</div>
              <div class="info-content">
                <div class="info-label">Amount</div>
                <div class="info-value amount">
                  IDR {{ formatNumber(getSelectedTransaction.amount) }}
                </div>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-icon">📝</div>
              <div class="info-content">
                <div class="info-label">Description</div>
                <div class="info-value description">
                  {{ getSelectedTransaction.description || '-' }}
                </div>
              </div>
            </div>

            <div class="info-row">
              <div class="info-icon">⏰</div>
              <div class="info-content">
                <div class="info-label">Created At</div>
                <div class="info-value time">
                  {{ getSelectedTransaction.created_at ? formatDateTime(getSelectedTransaction.created_at) : '-' }}
                </div>
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

    <!-- Modal form tambah kategori -->
    <div v-if="showAddCategoryForm" class="modal-overlay">
      <div class="modal-content">
        <h2>Add New Category</h2>
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label>Category Name</label>
            <input 
              type="text" 
              v-model="categoryForm.name"
              required
              placeholder="Enter category name"
            >
          </div>

          <div class="form-group">
            <label>Color</label>
            <input 
              type="color"
              v-model="categoryForm.color"
              class="color-input"
            >
          </div>

          <div class="form-actions">
            <button type="button" @click="showAddCategoryForm = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="save-btn">
              Add Category
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useTransactionStore } from '../stores/transaction'
import { useCategoryStore } from '../stores/category'
import { useAuthStore } from '../stores/auth'
import Chart from 'chart.js/auto'

export default {
  name: 'MainWorkspace',
  data() {
    return {
      startDate: '',
      endDate: '',
      showAddForm: false,
      editingTransaction: null,
      formData: {
        date: new Date().toISOString().split('T')[0],
        amount: '',
        description: '',
        category: ''
      },
      categories: [],
      categoryColors: [
        '#4CAF50',  // Green
        '#2196F3',  // Blue
        '#FFC107',  // Amber
        '#9C27B0',  // Purple
        '#F44336',  // Red
        '#009688',  // Teal
        '#FF9800',  // Orange
        '#03A9F4',  // Light Blue
        '#E91E63',  // Pink
        '#8BC34A',  // Light Green
        '#673AB7',  // Deep Purple
        '#00BCD4',  // Cyan
        '#FFEB3B',  // Yellow
        '#795548',  // Brown
        '#607D8B'   // Blue Grey
      ],
      pressTimer: null,
      pressedTransaction: null,
      selectedTransaction: null,
      transactions: [],
      showAddCategoryForm: false,
      categoryForm: {
        name: '',
        color: '#4CAF50'
      },
      editingCategoryId: null,
      editCategoryName: '',
      pieChart: null,
      lineChart: null
    }
  },
  computed: {
    visibleCategories() {
      return this.categories.filter(cat => cat.isVisible)
    },
    getSelectedTransaction() {
      return this.transactions.find(t => t.id === this.selectedTransaction) || {}
    },
    getTotalExpense() {
      return this.transactions.reduce((sum, t) => sum + Number(t.amount), 0)
    },
    getDailyExpenses() {
      const dailyData = {}
      this.transactions.forEach(t => {
        const date = t.date
        if (!dailyData[date]) {
          dailyData[date] = 0
        }
        dailyData[date] += Number(t.amount)
      })
      return dailyData
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
      console.log('Getting transactions for category:', categoryId)
      console.log('Current transactions state:', {
        all: this.transactions,
        length: this.transactions.length,
        isArray: Array.isArray(this.transactions),
        rawData: JSON.stringify(this.transactions)
      })
      
      if (!Array.isArray(this.transactions)) {
        console.warn('Transactions is not an array!')
        return []
      }
      
      const filtered = this.transactions.filter(t => {
        const matches = t && t.category === categoryId
        console.log('Checking transaction:', { 
          transaction: t, 
          categoryId, 
          transactionCategory: t?.category,
          matches,
          comparison: `${t?.category} === ${categoryId}`
        })
        return matches
      })
      
      console.log('Filtered transactions:', filtered)
      return filtered
    },
    getTotalByCategory(categoryId) {
      return this.getTransactionsByCategory(categoryId)
        .reduce((sum, t) => sum + (Number(t.amount) || 0), 0)
    },
    isOverBudget(categoryId) {
      const total = this.getTotalByCategory(categoryId)
      const BUDGET_LIMIT = 999999 // 1 juta rupiah
      return total > BUDGET_LIMIT
    },
    updateVisibleCategories() {
      localStorage.setItem('visibleCategories', JSON.stringify(this.categories))
    },
    async openAddTransaction(categoryId) {
      this.formData = {
        date: new Date().toISOString().split('T')[0],
        amount: '',
        description: '',
        category: categoryId
      }
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
      try {
        console.log('Fetching transactions with dates:', {
          startDate: this.startDate,
          endDate: this.endDate
        })
        
        const response = await transactionStore.fetchTransactions({
          startDate: this.startDate,
          endDate: this.endDate
        })
        
        console.log('Raw response from store:', response)
        
        if (response && Array.isArray(response)) {
          this.transactions = [...response]
          console.log('Transactions updated from array response')
        } else if (response && response.data && Array.isArray(response.data)) {
          this.transactions = [...response.data]
          console.log('Transactions updated from response.data')
        } else {
          console.warn('Unexpected response format:', response)
          this.transactions = []
        }
        
        console.log('Updated local transactions:', {
          transactions: this.transactions,
          length: this.transactions.length,
          sample: this.transactions[0]
        })
      } catch (error) {
        console.error('Error fetching transactions:', error)
        alert('Gagal mengambil data transaksi')
      }
    },
    async saveTransaction() {
      const transactionStore = useTransactionStore()
      try {
        if (!this.formData.date || !this.formData.amount || !this.formData.category) {
          alert('Mohon isi tanggal, jumlah, dan kategori')
          return
        }

        const transactionData = {
          ...this.formData,
          amount: Number(this.formData.amount),
          date: this.formData.date
        }

        console.log('Saving transaction:', {
          isEdit: !!this.editingTransaction,
          data: transactionData
        })

        let newTransaction
        if (this.editingTransaction) {
          newTransaction = await transactionStore.updateTransaction(
            this.editingTransaction.id,
            transactionData
          )
          console.log('Transaction updated:', newTransaction)
        } else {
          newTransaction = await transactionStore.addTransaction(transactionData)
          console.log('New transaction added:', newTransaction)
        }

        // Update date range if needed
        const transactionDate = new Date(transactionData.date)
        const startDate = new Date(this.startDate)
        const endDate = new Date(this.endDate)
        
        if (transactionDate > endDate) {
          this.endDate = transactionData.date
        }
        if (transactionDate < startDate) {
          this.startDate = transactionData.date
        }

        // Refresh data
        await this.fetchTransactions()
        
        this.showAddForm = false
        this.resetForm()
        
        alert(this.editingTransaction ? 'Transaksi berhasil diperbarui' : 'Transaksi berhasil ditambahkan')
      } catch (error) {
        console.error('Error saving transaction:', error)
        alert('Terjadi kesalahan saat menyimpan transaksi')
      }
    },
    async deleteTransaction(id) {
      if (confirm('Apakah Anda yakin ingin menghapus transaksi ini?')) {
        const transactionStore = useTransactionStore()
        try {
          await transactionStore.deleteTransaction(id)
          this.closePopup()
          await this.fetchTransactions() // Refresh data setelah menghapus
          alert('Transaksi berhasil dihapus')
        } catch (error) {
          console.error('Error deleting transaction:', error)
          alert('Gagal menghapus transaksi')
        }
      }
    },
    editTransaction(transaction) {
      this.editingTransaction = transaction
      this.formData = {
        date: transaction.date,
        amount: transaction.amount,
        category: transaction.category,
        description: transaction.description || ''
      }
      this.showAddForm = true
      this.closePopup() // Tutup popup detail setelah membuka form edit
    },
    resetForm() {
      this.formData = {
        date: new Date().toISOString().split('T')[0],
        amount: '',
        description: '',
        category: ''
      }
      this.editingTransaction = null
    },
    togglePopup(transactionId) {
      this.selectedTransaction = transactionId
      console.log('Selected transaction:', this.getSelectedTransaction)
    },
    closePopup() {
      this.selectedTransaction = null
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      return category ? category.name : '-'
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
    },
    getCategoryColor(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      return category?.color || this.getRandomColor()
    },
    getRandomColor() {
      const index = Math.floor(Math.random() * this.categoryColors.length)
      return this.categoryColors[index]
    },
    getContrastColor(hexcolor) {
      // Convert hex to RGB
      const r = parseInt(hexcolor.substring(1,3),16)
      const g = parseInt(hexcolor.substring(3,5),16)
      const b = parseInt(hexcolor.substring(5,7),16)
      
      // Calculate luminance
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
      
      // Return black or white based on luminance
      return luminance > 0.5 ? '#000000' : '#FFFFFF'
    },
    formatDateTime(datetime) {
      if (!datetime) return '-'
      const date = new Date(datetime)
      return new Intl.DateTimeFormat('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'Asia/Jakarta'
      }).format(date)
    },
    async updateCategoryColor(categoryId, newColor) {
      try {
        const categoryStore = useCategoryStore()
        await categoryStore.updateCategoryColor(categoryId, newColor)
        
        // Update local category color
        const category = this.categories.find(c => c.id === categoryId)
        if (category) {
          category.color = newColor
        }
      } catch (error) {
        console.error('Error updating category color:', error)
        alert('Gagal mengubah warna kategori')
      }
    },
    async saveCategory() {
      try {
        const categoryStore = useCategoryStore()
        await categoryStore.addCategory(this.categoryForm)
        
        // Refresh categories
        await categoryStore.fetchCategories()
        
        // Update local categories
        this.categories = categoryStore.categories.map(cat => ({
          ...cat,
          isVisible: true
        }))
        
        this.showAddCategoryForm = false
        this.categoryForm = { name: '', color: '#4CAF50' }
        
        alert('Category added successfully!')
      } catch (error) {
        console.error('Error saving category:', error)
        alert('Failed to add category')
      }
    },
    async confirmDeleteCategory(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      const transactions = this.getTransactionsByCategory(categoryId)
      
      if (transactions.length > 0) {
        const confirm = window.confirm(
          `Category "${category.name}" has ${transactions.length} transactions. ` +
          'Deleting this category will also delete all associated transactions. ' +
          'Are you sure you want to continue?'
        )
        if (!confirm) return
      } else {
        const confirm = window.confirm(
          `Are you sure you want to delete category "${category.name}"?`
        )
        if (!confirm) return
      }
      
      try {
        const categoryStore = useCategoryStore()
        await categoryStore.deleteCategory(categoryId)
        
        // Refresh data
        await categoryStore.fetchCategories()
        this.categories = categoryStore.categories.map(cat => ({
          ...cat,
          isVisible: true
        }))
        
        // Refresh transactions karena mungkin ada yang terhapus
        await this.fetchTransactions()
        
      } catch (error) {
        console.error('Error deleting category:', error)
        alert('Failed to delete category')
      }
    },
    startEditCategory(category) {
      this.editingCategoryId = category.id
      this.editCategoryName = category.name
      this.$nextTick(() => {
        if (this.$refs.categoryNameInput) {
          this.$refs.categoryNameInput.focus()
          this.$refs.categoryNameInput.select()
        }
      })
    },
    async saveCategoryName(categoryId) {
      try {
        if (!this.editCategoryName.trim()) {
          this.cancelEditCategory()
          return
        }

        const categoryStore = useCategoryStore()
        await categoryStore.updateCategory(categoryId, {
          name: this.editCategoryName.trim()
        })

        // Update local category name
        const category = this.categories.find(c => c.id === categoryId)
        if (category) {
          category.name = this.editCategoryName.trim()
        }

        this.editingCategoryId = null
        this.editCategoryName = ''
      } catch (error) {
        console.error('Error updating category name:', error)
        // Kembalikan nama kategori ke nilai sebelumnya
        const category = this.categories.find(c => c.id === categoryId)
        if (category) {
          category.name = category.name
        }
      }
    },
    cancelEditCategory() {
      this.editingCategoryId = null
      this.editCategoryName = ''
    },
    calculatePercentage(amount) {
      const total = this.getTotalExpense
      if (total === 0) return 0
      return ((amount / total) * 100).toFixed(1)
    },
    initPieChart() {
      const canvas = this.$refs.pieChartContainer
      if (!canvas) return

      if (this.pieChart) {
        this.pieChart.destroy()
      }

      const data = this.visibleCategories
        .map(cat => ({
          value: this.getTotalByCategory(cat.id),
          color: cat.color,
          name: cat.name
        }))
        .filter(d => d.value > 0)

      if (data.length === 0) return

      this.pieChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
          labels: data.map(d => d.name),
          datasets: [{
            data: data.map(d => d.value),
            backgroundColor: data.map(d => d.color),
            borderWidth: 2,
            borderColor: '#ffffff',
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const value = context.raw
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${context.label}: IDR ${this.formatNumber(value)} (${percentage}%)`
                }
              }
            }
          }
        }
      })
    },
    initLineChart() {
      this.$nextTick(() => {
        const canvas = this.$refs.lineChartContainer
        if (!canvas) {
          console.error('Canvas element not found')
          return
        }

        if (this.lineChart) {
          this.lineChart.destroy()
        }

        const dailyData = this.getDailyExpenses
        const dates = Object.keys(dailyData).sort()

        if (dates.length === 0) {
          console.log('No data to display')
          return
        }

        try {
          this.lineChart = new Chart(canvas, {
            type: 'line',
            data: {
              labels: dates.map(d => this.formatDate(d)),
              datasets: [{
                label: 'Pengeluaran Harian',
                data: dates.map(d => dailyData[d]),
                borderColor: '#2196F3',
                backgroundColor: '#2196F3',
                tension: 0.4,
                pointRadius: 4
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    callback: value => `IDR ${this.formatNumber(value)}`
                  }
                }
              }
            }
          })
        } catch (error) {
          console.error('Error creating line chart:', error)
        }
      })
    },
    updateCharts() {
      this.$nextTick(() => {
        if (this.$refs.pieChartContainer) {
          this.initPieChart();
        }
        if (this.$refs.lineChartContainer) {
          this.initLineChart();
        }
      });
    }
  },
  watch: {
    transactions: {
      immediate: true,
      handler(newTransactions) {
        console.log('Transactions changed:', newTransactions)
        if (newTransactions && newTransactions.length > 0) {
          this.$nextTick(() => {
            this.updateCharts()
          })
        }
      },
      deep: true
    },
    visibleCategories: {
      handler() {
        this.updateCharts();
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.updateCharts();
    });
  },
  async created() {
    const authStore = useAuthStore()
    const transactionStore = useTransactionStore()
    const categoryStore = useCategoryStore()
    
    try {
      if (!authStore.initAuth()) {
        console.log('No auth found, redirecting to login...')
        this.$router.push('/login')
        return
      }

      console.log('Initializing workspace...')
      
      // Set default date range to current month
      const today = new Date()
      const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
      
      if (!this.startDate || !this.endDate) {
        // Set startDate to first day of current month
        this.startDate = new Date(today.getFullYear(), today.getMonth(), 1)
          .toISOString().split('T')[0]
        
        // Set endDate to last day of current month
        this.endDate = lastDayOfMonth.toISOString().split('T')[0]
      }

      console.log('Date range:', { startDate: this.startDate, endDate: this.endDate })
      
      // Fetch data
      await Promise.all([
        categoryStore.fetchCategories(),
        this.fetchTransactions()
      ])
      
      this.categories = categoryStore.categories.map(cat => ({
        ...cat,
        isVisible: true
      }))
      
    } catch (error) {
      console.error('Error initializing workspace:', error)
      if (error.response?.status === 401) {
        authStore.logout()
      } else {
        alert('Terjadi kesalahan saat memuat data')
      }
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
  background: white;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
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
  color: #000000;
  font-weight: 500;
  cursor: pointer;
}

.color-picker {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.color-input {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: none;
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: 2px solid #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Animasi hover untuk color picker */
.color-input:hover {
  transform: scale(1.1);
}

/* Styling untuk mobile */
@media (max-width: 768px) {
  .category-item {
    padding: 0.5rem;
  }
  
  .color-input {
    width: 20px;
    height: 20px;
  }
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
  background: #000000;
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

.info-row {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  margin-bottom: 15px;
}

.info-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 12px;
  font-size: 20px;
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
  display: flex;
  gap: 12px;
  margin-top: 20px;
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
  border: 1px solid rgba(239, 68, 68, 0.2) !important;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.15);
}

.over-budget .category-title {
  background: rgba(254, 226, 226, 0.9);
}

.over-budget .transaction-list {
  background: rgba(254, 242, 242, 0.5);
}

.over-budget .transaction-item {
  background: rgba(255, 255, 255, 0.9);
  border-color: #ef4444;
}

.over-budget .transaction-item:hover {
  background: rgba(254, 226, 226, 0.2);
  border-left: 4px solid #ef4444;
}

.over-budget .total-amount {
  color: #ef4444 !important;
}

.over-budget .total-amount::before {
  content: '⚠️';
}

.over-budget .add-btn {
  background: linear-gradient(45deg, #ef4444, #dc2626) !important;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
}

.over-budget .add-btn:hover {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
}

.info-value.time {
  font-size: 0.95rem;
  color: #64748b;
}

.info-icon.time {
  background: #f8fafc;
  color: #64748b;
}

.categories-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin: 1rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  backdrop-filter: blur(8px);
}

.add-category-btn {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
}

.add-category-btn .btn-icon {
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1;
}

.add-category-btn .btn-text {
  letter-spacing: 0.5px;
}

.add-category-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
  background: linear-gradient(135deg, #45a049, #388e3c);
}

.add-category-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(76, 175, 80, 0.2);
}

.category-actions {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
}

.delete-category-btn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: none;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.delete-category-btn:hover {
  transform: scale(1.1);
  background: #fee2e2;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.category-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-right: 7rem; /* Memberikan ruang untuk tombol */
}

.category-name {
  margin: 0;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.category-name:hover {
  background: rgba(0, 0, 0, 0.05);
}

.edit-category-name {
  margin: 0;
  padding: 0;
}

.edit-category-input {
  font-size: 1.17em;  /* Sama dengan ukuran h3 */
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border: 2px solid;
  border-radius: 4px;
  width: 200px;
  outline: none;
  transition: all 0.2s;
}

.edit-category-input:focus {
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
}

.statistics-section {
  margin-bottom: 1.5rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  background-image: 
    radial-gradient(circle at 10px 10px, rgba(33, 150, 243, 0.05) 2px, transparent 0),
    linear-gradient(to right, rgba(33, 150, 243, 0.03), rgba(33, 150, 243, 0.08));
  background-size: 20px 20px, 100% 100%;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 
    0 2px 12px rgba(0,0,0,0.06),
    inset 0 -2px 8px rgba(33, 150, 243, 0.1);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, transparent 100%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(33, 150, 243, 0.03) 10px,
      rgba(33, 150, 243, 0.03) 20px
    );
  opacity: 0.5;
  z-index: 0;
}

.total-overview {
  text-align: center;
  position: relative;
  transition: transform 0.3s ease;
}

.total-overview:hover {
  transform: translateY(-2px);
}

.total-amount-large {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2196F3;
  margin: 1.5rem 0;
  text-shadow: 2px 2px 4px rgba(33, 150, 243, 0.2);
  position: relative;
  z-index: 1;
  animation: pulse 3s infinite ease-in-out;
}

.stat-period {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
  position: relative;
  z-index: 1;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  display: inline-block;
  backdrop-filter: blur(4px);
}

h3 {
  color: #1e293b;
  font-weight: 600;
  margin: 0;
  position: relative;
  z-index: 1;
}

/* Tambahkan animasi subtle */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

.total-amount-large {
  animation: pulse 3s infinite ease-in-out;
}

.category-headers {
  position: relative;
  margin-bottom: 1rem;
}

.category-headers-actions {
  position: absolute;
  top: -3.5rem;  /* Sesuaikan jarak dari atas */
  left: 1rem;
  z-index: 10;
}

.add-category-btn {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
}

.add-category-btn .btn-icon {
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1;
}

.add-category-btn .btn-text {
  letter-spacing: 0.5px;
}

.add-category-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
  background: linear-gradient(135deg, #45a049, #388e3c);
}

.add-category-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(76, 175, 80, 0.2);
}
</style> 