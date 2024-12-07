<template>
  <div class="form-container">
    <div class="form-card">
      <h2>{{ isEdit ? 'Edit Transaksi' : 'Tambah Transaksi' }}</h2>
      
      <form @submit.prevent="handleSubmit" class="transaction-form">
        <div class="form-group">
          <label for="category">Kategori</label>
          <select 
            id="category"
            v-model="form.category"
            required
          >
            <option value="A">Kategori A</option>
            <option value="B">Kategori B</option>
            <option value="C">Kategori C</option>
          </select>
        </div>

        <div class="form-group">
          <label for="amount">Jumlah</label>
          <input 
            type="number"
            id="amount"
            v-model="form.amount"
            required
          />
        </div>

        <div class="form-group">
          <label for="description">Deskripsi</label>
          <textarea 
            id="description"
            v-model="form.description"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="date">Tanggal</label>
          <input 
            type="date"
            id="date"
            v-model="form.date"
            required
          />
        </div>

        <div class="button-group">
          <button type="button" @click="$router.push('/workspace')" class="cancel-button">
            Batal
          </button>
          <button type="submit" class="save-button">
            {{ isEdit ? 'Update' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TransactionForm',
  data() {
    return {
      form: {
        category: '',
        amount: '',
        description: '',
        date: ''
      },
      isEdit: false
    }
  },
  created() {
    const id = this.$route.query.id
    if (id) {
      this.isEdit = true
    }
  },
  methods: {
    async handleSubmit() {
      try {
        this.$router.push('/workspace')
      } catch (err) {
        alert('Terjadi kesalahan. Silakan coba lagi.')
      }
    }
  }
}
</script>

<style scoped>
/* Style yang sudah ada tetap sama */
</style> 