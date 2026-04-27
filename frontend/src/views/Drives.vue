<template>
  <div class="container py-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold text-primary mb-0">Open drives on FirstPlace</h3>
      <input 
        type="text" 
        class="form-control w-auto" 
        placeholder="Search jobs or companies..." 
        v-model="search" 
        @input="fetchDrives"
        style="min-width: 250px;"
      />
    </div>

    <div class="row g-4" v-if="drives.length">

      <div class="col-md-6 col-lg-4" v-for="d in drives" :key="d.id">
        <div class="card h-100 border border-dark rounded-4 shadow-sm">

          <div class="card-body d-flex flex-column">

            <h5 class="fw-semibold mb-2">{{ d.job_title }}</h5>

            <p class="text-muted mb-1">{{ d.company_name }}</p>
            <p class="mb-2" v-if="d.company_blacklisted"><span class="badge bg-dark">Company blacklisted</span></p>

            <div class="small text-secondary mb-3">
              <div>Minimum CGPA: <strong>{{ d.min_cgpa }}</strong></div>
              <div>Apply Before: <strong>{{ formatDate(d.application_deadline) }}</strong></div>
            </div>

            <div class="mt-auto">
              <router-link 
                :to="`/drives/${d.id}`" 
                class="btn btn-primary btn-sm w-100"
              >
                View Details
              </router-link>
            </div>

          </div>

        </div>
      </div>

    </div>

    <div v-else class="text-center text-muted py-5">
      No opportunities available at the moment
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const drives = ref([])
const search = ref('')

const fetchDrives = async () => {
  const params = search.value ? { search: search.value } : {}
  const res = await api.get('/drives', { params })
  drives.value = res.data
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '-'

onMounted(fetchDrives)
</script>