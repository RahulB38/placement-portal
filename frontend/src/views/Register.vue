<template>
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <div class="col-md-8 col-lg-6">
      <div class="card shadow border-0 rounded-4">
        <div class="card-body p-4">

          <h3 class="text-center mb-4 fw-bold text-primary">Join FirstPlace</h3>

          <div v-if="error" class="alert alert-danger">
            <h6 class="alert-heading fw-bold mb-1">Registration error</h6>
            <p class="mb-0 small">{{ error }}</p>
          </div>

          <form @submit.prevent="register">

            <div class="mb-3">
              <label class="form-label">Email Address</label>
              <input type="email" class="form-control" v-model="email" required />
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required minlength="6" />
            </div>

            <template v-if="type === 'student'">

              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="name" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Roll Number</label>
                <input type="text" class="form-control" v-model="roll_number" required />
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Branch</label>
                  <select class="form-select" v-model="branch" required>
                    <option value="" disabled>Select branch</option>
                    <option v-for="b in branchOptions" :key="b" :value="b">{{ b }}</option>
                  </select>
                </div>

                <div class="col-md-3 mb-3">
                  <label class="form-label">Year</label>
                  <select class="form-select" v-model.number="year" required>
                    <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                  </select>
                </div>

                <div class="col-md-3 mb-3">
                  <label class="form-label">CGPA</label>
                  <input type="number" step="0.01" class="form-control" v-model="cgpa" required min="0" max="10" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Phone (10 digits, optional)</label>
                <input type="text" class="form-control" v-model="phone" maxlength="10" pattern="[0-9]*"
                  inputmode="numeric" />
              </div>

            </template>

            <template v-else>

              <div class="mb-3">
                <label class="form-label">Company Name</label>
                <input type="text" class="form-control" v-model="company_name" required />
              </div>

              <div class="mb-3">
                <label class="form-label">HR Contact</label>
                <input type="text" class="form-control" v-model="hr_contact" required />
              </div>

              <div class="mb-3">
                <label class="form-label">HR Email</label>
                <input type="email" class="form-control" v-model="hr_email" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Website</label>
                <input type="url" class="form-control" v-model="website" />
              </div>

            </template>

            <button type="submit" class="btn btn-primary w-100 mt-2" :disabled="loading">
              {{ loading ? 'Processing...' : 'Register' }}
            </button>

          </form>

          <div class="text-center mt-3">
            <button class="btn btn-link text-decoration-none"
              @click="type = type === 'student' ? 'company' : 'student'">
              {{ type === 'student' ? 'Register as Company' : 'Register as Student' }}
            </button>
          </div>

          <p class="mt-3 text-center">
            Already have an account?
            <router-link to="/login" class="text-primary">Login</router-link>
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
const type = ref('student')
const email = ref('')
const password = ref('')
const name = ref('')
const roll_number = ref('')
const branchOptions = ['CSE', 'IT', 'ECE', 'EEE', 'Mechanical', 'DS', 'AI', 'Robotics', 'Civil', 'Other']
const yearOptions = [1, 2, 3, 4]
const branch = ref('')
const year = ref(3)
const cgpa = ref(0)
const phone = ref('')
const company_name = ref('')
const hr_contact = ref('')
const hr_email = ref('')
const website = ref('')
const error = ref('')
const loading = ref(false)

const register = async () => {
  error.value = ''
  loading.value = true
  try {
    if (type.value === 'student') {
      await api.post('/auth/register/student', {
        email: email.value,
        password: password.value,
        name: name.value,
        roll_number: roll_number.value,
        branch: branch.value,
        year: year.value,
        cgpa: parseFloat(cgpa.value),
        phone: phone.value || undefined
      })
    } else {
      await api.post('/auth/register/company', {
        email: email.value,
        password: password.value,
        company_name: company_name.value,
        hr_contact: hr_contact.value,
        hr_email: hr_email.value,
        website: website.value || undefined
      })
    }
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>