<template>
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <div class="col-md-6 col-lg-5">
      <div class="card border shadow-sm rounded-3">
        <div class="card-body p-4">
          <h3 class="text-center mb-3 fw-bold text-primary">FirstPlace login</h3>

          <div v-if="error" class="alert alert-danger">
            <h6 class="alert-heading fw-bold mb-1">Login error</h6>
            <p class="mb-0 small">{{ error }}</p>
          </div>

          <form @submit.prevent="login">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="email" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required />
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">{{ loading ? 'Please wait...' : 'Login' }}</button>
          </form>

          <p class="mt-3 text-center small">
            <router-link to="/register">Create account</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
  error.value = ''
  loading.value = true
  try {
    await api.post('/auth/login', { email: email.value, password: password.value, remember: false })
    const res = await api.get('/auth/me')
    const role = res.data.role
    if (role === 'admin') router.push('/admin')
    else if (role === 'company') router.push('/company')
    else if (role === 'student') router.push('/student')
    else router.push('/')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
