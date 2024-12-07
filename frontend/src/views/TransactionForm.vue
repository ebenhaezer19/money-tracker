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
            <option value="">Pilih Kategori</option>
            <option v-for="category in categories" 
                    :key="category.id_category" 
                    :value="category.id_category">
              {{ category.title }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="amount">Jumlah Pengeluaran</label>
          <input 
            type="number"
            id="amount"
            v-model="form.amount"
            min="0"
            step="1000"
            required
          />
        </div>

        <div class="form-group">
          <label for="description">Deskripsi</label>
          <textarea 
            id="description"
            v-model="form.description"
            rows="3"
            maxlength="128"
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
          <button type="submit" class="save-button" :disabled="isLoading">
            {{ isLoading ? 'Menyimpan...' : (isEdit ? 'Update' : 'Simpan') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useTransactionStore } from '../stores/transaction'

export default {
  name: 'TransactionForm',
  data() {
    return {
      form: {
        category: '',
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0]
      },
      isEdit: false,
      isLoading: false
    }
  },
  computed: {
    categories() {
      return useTransactionStore().categories
    }
  },
  async created() {
    await useTransactionStore().fetchCategories()
    
    const id = this.$route.query.id
    if (id) {
      this.isEdit = true
      this.loadTransaction(id)
    }
  },
  methods: {
    async loadTransaction(id) {
      try {
        const transaction = this.transactions.find(t => t.id_transaction === id)
        if (transaction) {
          this.form = {
            category: transaction.id_category,
            amount: transaction.amount,
            description: transaction.description,
            date: new Date(transaction.timestamp).toISOString().split('T')[0]
          }
        }
      } catch (error) {
        console.error('Error loading transaction:', error)
      }
    },
    async handleSubmit() {
      this.isLoading = true
      try {
        const store = useTransactionStore()
        const data = {
          ...this.form,
          amount: Number(this.form.amount)
        }
        
        if (this.isEdit) {
          await store.editTransaction(this.$route.query.id, data)
        } else {
          await store.addTransaction(data)
        }
        
        this.$router.push('/workspace')
      } catch (error) {
        console.error('Error saving transaction:', error)
        alert('Gagal menyimpan transaksi. Silakan coba lagi.')
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.form-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: #f5f5f5;
}

.form-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.transaction-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

input, select, textarea {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea {
  resize: vertical;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.save-button, .cancel-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  flex: 1;
}

.save-button {
  background-color: #4CAF50;
  color: white;
}

.save-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #9e9e9e;
  color: white;
}
</style> 