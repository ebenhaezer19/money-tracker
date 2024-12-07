<template>
  <div class="workspace-container">
    <header class="header">
      <h1>Finance Tracker</h1>
      <button @click="handleLogout" class="logout-button">Logout</button>
    </header>

    <div class="filters">
      <div class="filter-group">
        <label>Kategori:</label>
        <select v-model="selectedCategory">
          <option value="">Semua</option>
          <option value="A">Kategori A</option>
          <option value="B">Kategori B</option>
          <option value="C">Kategori C</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Tanggal:</label>
        <input type="date" v-model="startDate">
        <span>sampai</span>
        <input type="date" v-model="endDate">
      </div>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Kategori</th>
            <th>Jumlah</th>
            <th>Tanggal</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="transaction in transactions" :key="transaction.id"
              :class="{ 'over-budget': transaction.isOverBudget }">
            <td>{{ transaction.category }}</td>
            <td>Rp {{ transaction.amount.toLocaleString() }}</td>
            <td>{{ formatDate(transaction.date) }}</td>
            <td>
              <button @click="editTransaction(transaction)" class="edit-button">Edit</button>
              <button @click="deleteTransaction(transaction.id)" class="delete-button">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <button @click="$router.push('/transaction')" class="add-button">
      + Tambah Transaksi
    </button>
  </div>
</template>

<script>
export default {
  name: 'MainWorkspace',
  data() {
    return {
      selectedCategory: '',
      startDate: '',
      endDate: '',
      transactions: [
        {
          id: 1,
          category: 'A',
          amount: 1000000,
          date: '2024-03-20',
          isOverBudget: true
        }
      ]
    }
  },
  methods: {
    formatDate(date) {
      return new Date(date).toLocaleDateString('id-ID')
    },
    handleLogout() {
      localStorage.removeItem('isAuthenticated')
      this.$router.push('/')
    },
    editTransaction(transaction) {
      this.$router.push({
        path: '/transaction',
        query: { id: transaction.id }
      })
    },
    deleteTransaction(id) {
      confirm('Yakin ingin menghapus transaksi ini?')
    }
  }
}
</script>

<style scoped>
/* Style yang sudah ada tetap sama */
</style> 