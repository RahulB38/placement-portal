<template>
  <div class="container py-3">
    <div v-if="drive" class="card border shadow-sm">
      <div class="card-body">
        <h3 class="mb-2 text-primary">{{ drive.job_title }}</h3>
        <p class="text-muted mb-2">{{ drive.company_name }}</p>
        <p class="mb-2" v-if="drive.company_blacklisted"><span class="badge bg-dark">This company is blacklisted on FirstPlace</span></p>
        <p class="mb-2"><strong>About role</strong></p>
        <p>{{ drive.job_description }}</p>
        <p><strong>Min CGPA:</strong> {{ drive.min_cgpa }}</p>
        <p><strong>Branches:</strong> {{ drive.eligibility_branches || 'As per drive' }}</p>
        <p><strong>Deadline:</strong> {{ formatDate(drive.application_deadline) }}</p>
        <p v-if="drive.package_info"><strong>Package:</strong> {{ drive.package_info }}</p>
        <router-link to="/drives" class="btn btn-outline-primary mt-2">Back</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const drive = ref(null)

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '-'

onMounted(async () => {
  const res = await api.get(`/drives/${route.params.id}`)
  drive.value = res.data
})
</script>
