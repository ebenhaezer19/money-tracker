<template>
  <div class="workspace-container">
    <header class="header">
      <h1>Money Tracker</h1>
      <div class="user-info">
        <span>{{ user?.username }}</span>
        <button @click="handleLogout" class="logout-button">Logout</button>
      </div>
    </header>

    <div class="content">
      <aside class="sidebar">
        <div class="categories">
          <h3>Kategori</h3>
          <ul>
            <li 
              v-for="category in categories" 
              :key="category.id_category"
              :class="{ active: selectedCategory === category.id_category }"
              @click="selectCategory(category)"
            >
              {{ category.title }}
              <button @click.stop="editCategory(category)" class="edit-icon">✏️</button>
              <button @click.stop="hideCategory(category.id_category)" class="hide-icon">👁️</button>
            </li>
          </ul>
        </div>

        <div class="date-filter">
          <h3>Filter Tanggal</h3>
          <div class="date-inputs">
            <input type="date" v-model="startDate" @change="fetchTransactions">
            <span>sampai</span>
            <input type="date" v-model="endDate" @change="fetchTransactions">
          </div>
        </div>
      </aside>

      <main class="main-content">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Kategori</th>
                <th>Jumlah</th>
                <th>Tanggal</th>
                <th>Deskripsi</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="transaction in transactions" 
                :key="transaction.id_transaction"
              >
                <td>{{ getCategoryTitle(transaction.id_category) }}</td>
                <td>Rp {{ formatNumber(transaction.amount) }}</td>
                <td>{{ formatDate(transaction.timestamp) }}</td>
                <td>{{ transaction.description }}</td>
                <td>
                  <button @click="editTransaction(transaction)" class="edit-button">Edit</button>
                  <button @click="deleteTransaction(transaction.id_transaction)" class="delete-button">Hapus</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <button @click="$router.push('/transaction')" class="add-button">
          + Tambah Transaksi
        </button>
      </main>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/auth'
import { useTransactionStore } from '../stores/transaction'

export default {
  name: 'MainWorkspace',
  data() {
    return {
      selectedCategory: null,
      startDate: '',
      endDate: '',
      isLoading: false
    }
  },
  computed: {
    user() {
      return useAuthStore().user
    },
    transactions() {
      return useTransactionStore().transactions
    },
    categories() {
      return useTransactionStore().categories
    }
  },
  methods: {
    async fetchTransactions() {
      const filters = {
        userId: this.user.id_user,
        categoryId: this.selectedCategory,
        dateBegin: this.startDate,
        dateEnd: this.endDate
      }
      
      try {
        await useTransactionStore().fetchTransactions(filters)
      } catch (error) {
        console.error('Error fetching transactions:', error)
      }
    },
    formatNumber(value) {
      return value.toLocaleString('id-ID')
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('id-ID')
    },
    getCategoryTitle(categoryId) {
      const category = this.categories.find(c => c.id_category === categoryId)
      return category ? category.title : '-'
    },
    async deleteTransaction(transactionId) {
      if (confirm('Yakin ingin menghapus transaksi ini?')) {
        try {
          await useTransactionStore().deleteTransaction(transactionId)
          await this.fetchTransactions()
        } catch (error) {
          console.error('Error deleting transaction:', error)
        }
      }
    },
    editTransaction(transaction) {
      this.$router.push({
        path: '/transaction',
        query: { id: transaction.id_transaction }
      })
    },
    selectCategory(category) {
      this.selectedCategory = category.id_category
      this.fetchTransactions()
    },
    async handleLogout() {
      try {
        await useAuthStore().logout()
        this.$router.push('/')
      } catch (error) {
        console.error('Error logging out:', error)
      }
    }
  },
  async created() {
    await Promise.all([
      useTransactionStore().fetchCategories(),
      this.fetchTransactions()
    ])
  }
}
</script>

<style scoped>
.content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;
  padding: 2rem;
}

.sidebar {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.categories ul {
  list-style: none;
  padding: 0;
}

.categories li {
  padding: 0.5rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.categories li.active {
  background-color: #e3f2fd;
}

.edit-icon, .hide-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
}

.date-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.table-container {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.edit-button, .delete-button {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.edit-button {
  background-color: #2196F3;
  color: white;
}

.delete-button {
  background-color: #f44336;
  color: white;
}

.add-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background-color: #4CAF50;
  color: white;
  padding: 1rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style> 