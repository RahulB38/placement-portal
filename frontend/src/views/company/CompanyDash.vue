<template>
  <div class="container-fluid px-3 py-3">

    <h3 class="fw-bold text-primary mb-1" v-if="company">Welcome {{ company.company_name }}</h3>
    <p class="text-muted small mb-3 mb-md-4">Total applicants across your drives: {{ totalApplicants }}</p>

    <div class="row g-4">
      <aside class="col-12 col-md-3 col-lg-2">
        <nav class="nav flex-column nav-pills dashboard-sidebar" aria-label="Company sections">
          <a class="nav-link" :class="{ active: tab === 'drives' }" href="#" @click.prevent="tab = 'drives'">My drives</a>
          <a class="nav-link" :class="{ active: tab === 'create' }" href="#" @click.prevent="tab = 'create'">Create drive</a>
          <a class="nav-link" :class="{ active: tab === 'applications' }" href="#" @click.prevent="tab = 'applications'">Manage applications</a>
        </nav>
      </aside>
      <div class="col-12 col-md-9 col-lg-10 min-w-0">

    <div v-if="tab === 'drives'" class="card border shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Job</th>
                <th>Status</th>
                <th>Deadline</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in drives" :key="d.id">
                <td>{{ d.job_title }}</td>
                <td>
                  <span class="badge" :class="d.status === 'approved' ? 'bg-success' : d.status === 'pending' ? 'bg-warning text-dark' : 'bg-secondary'">{{ d.status }}</span>
                </td>
                <td>{{ formatDate(d.deadline) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="tab === 'create'" class="card border shadow-sm">
      <div class="card-body">
        <div v-if="createError" class="alert alert-danger small">{{ createError }}</div>
        <form @submit.prevent="createDrive">
          <div class="mb-3">
            <label class="form-label">Job title</label>
            <input type="text" class="form-control" v-model="form.job_title" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Job description</label>
            <textarea class="form-control" v-model="form.job_description" rows="3" required></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Minimum CGPA</label>
            <input type="number" step="0.01" class="form-control" v-model="form.min_cgpa" min="0" max="10" required />
          </div>
          <div class="mb-3">
            <label class="form-label d-block">Eligible branches (select one or more)</label>
            <div class="row g-2">
              <div class="col-md-4 col-6" v-for="b in branchOptions" :key="b">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" :id="`br-${b}`" :value="b" v-model="form.eligibility_branches" />
                  <label class="form-check-label small" :for="`br-${b}`">{{ b }}</label>
                </div>
              </div>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label d-block">Eligible years (select one or more)</label>
            <div class="d-flex flex-wrap gap-3">
              <div class="form-check" v-for="y in yearOptions" :key="y">
                <input class="form-check-input" type="checkbox" :id="`yr-${y}`" :value="y" v-model="form.eligible_years" />
                <label class="form-check-label small" :for="`yr-${y}`">Year {{ y }}</label>
              </div>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Deadline</label>
            <input type="datetime-local" class="form-control" v-model="form.application_deadline" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Package info</label>
            <input type="text" class="form-control" v-model="form.package_info" />
          </div>
          <button type="submit" class="btn btn-primary">Submit drive</button>
        </form>
      </div>
    </div>

    <div v-if="tab === 'applications'" class="card border shadow-sm">
      <div class="card-body">
        <h6 class="fw-semibold mb-3">Jobs</h6>
        <div class="table-responsive mb-3">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Job</th>
                <th>Applicants</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in drives" :key="d.id">
                <td>{{ d.job_title }}</td>
                <td>{{ d.applicants_count }}</td>
                <td>
                  <button type="button" class="btn btn-sm btn-primary" @click="viewApplications(d.id)">View applications</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="selectedDriveTitle" class="mt-2">
          <h6 class="fw-semibold mb-2">All applications — {{ selectedDriveTitle }}</h6>
          <div v-if="statusMessage" class="alert py-2 mb-3 small" :class="statusMessageIsError ? 'alert-danger' : 'alert-success'">{{ statusMessage }}</div>
          <div v-if="applications.length === 0" class="text-muted small">No rows yet</div>
          <div v-else class="table-responsive">
            <table class="table table-sm table-bordered align-middle">
              <thead class="table-light">
                <tr>
                  <th>Student</th>
                  <th>Roll</th>
                  <th>Branch</th>
                  <th>CGPA</th>
                  <th>Resume</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in applications" :key="a.id">
                  <td>{{ a.student_name }}</td>
                  <td>{{ a.roll_number }}</td>
                  <td>{{ a.branch }}</td>
                  <td>{{ a.cgpa }}</td>
                  <td>
                    <a
                      v-if="a.has_resume"
                      class="small"
                      :href="`/api/company/applications/${a.id}/resume`"
                      target="_blank"
                      rel="noopener noreferrer"
                    >View PDF</a>
                    <span v-else class="text-muted small">—</span>
                  </td>
                  <td>
                    <span v-if="editingAppId !== a.id" class="badge" :class="statusBadgeClass(a.status)">{{ a.status }}</span>
                    <select v-else class="form-select form-select-sm" v-model="statusDraft" style="max-width: 200px;">
                      <option value="applied">applied</option>
                      <option value="shortlisted">shortlisted</option>
                      <option value="selected">selected</option>
                      <option value="rejected">rejected</option>
                    </select>
                  </td>
                  <td>
                    <template v-if="editingAppId !== a.id">
                      <button type="button" class="btn btn-sm btn-outline-primary" @click="startStatusEdit(a)">Update</button>
                    </template>
                    <template v-else>
                      <button type="button" class="btn btn-sm btn-success me-1" @click="saveStatus(a)">Save</button>
                      <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelStatusEdit">Cancel</button>
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../../api'

const tab = ref('drives')
const company = ref(null)
const drives = ref([])
const totalApplicants = ref(0)
const applications = ref([])
const selectedDriveTitle = ref('')
const editingAppId = ref(null)
const statusDraft = ref('applied')
const statusMessage = ref('')
const statusMessageIsError = ref(false)
const createError = ref('')
const branchOptions = ['CSE', 'IT', 'ECE', 'EEE', 'Mechanical', 'DS', 'AI', 'Robotics', 'Civil', 'Other']
const yearOptions = ['1', '2', '3', '4']
const form = ref({
  job_title: '',
  job_description: '',
  min_cgpa: 0,
  eligibility_branches: [],
  eligible_years: ['3', '4'],
  application_deadline: '',
  package_info: ''
})

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '-'

const statusBadgeClass = (s) => {
  if (s === 'selected') return 'bg-success'
  if (s === 'shortlisted') return 'bg-info text-dark'
  if (s === 'rejected') return 'bg-danger'
  return 'bg-secondary'
}

const startStatusEdit = (a) => {
  statusMessage.value = ''
  statusMessageIsError.value = false
  editingAppId.value = a.id
  statusDraft.value = a.status
}

const cancelStatusEdit = () => {
  editingAppId.value = null
}

const saveStatus = async (a) => {
  statusMessage.value = ''
  try {
    await api.put(`/company/applications/${a.id}/status`, { status: statusDraft.value })
    a.status = statusDraft.value
    editingAppId.value = null
    statusMessage.value = 'Status updated successfully.'
    statusMessageIsError.value = false
  } catch (e) {
    statusMessage.value = e.response?.data?.error || 'Could not update status'
    statusMessageIsError.value = true
  }
}

const fetchDashboard = async () => {
  const res = await api.get('/company/dashboard')
  company.value = res.data.company
  drives.value = res.data.drives
  totalApplicants.value = res.data.total_applicants
}

const createDrive = async () => {
  createError.value = ''
  try {
    await api.post('/company/drives', {
      ...form.value,
      eligibility_branches: form.value.eligibility_branches,
      eligible_years: form.value.eligible_years,
      application_deadline: new Date(form.value.application_deadline).toISOString()
    })
    form.value = { job_title: '', job_description: '', min_cgpa: 0, eligibility_branches: [], eligible_years: ['3', '4'], application_deadline: '', package_info: '' }
    tab.value = 'drives'
    fetchDashboard()
  } catch (e) {
    createError.value = e.response?.data?.error || 'Save failed'
  }
}

const viewApplications = async (driveId) => {
  editingAppId.value = null
  statusMessage.value = ''
  const d = drives.value.find(x => x.id === driveId)
  selectedDriveTitle.value = d?.job_title || ''
  applications.value = []
  try {
    const res = await api.get(`/company/drives/${driveId}/applications`)
    applications.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    applications.value = []
  }
}

watch(tab, (t) => {
  if (t !== 'applications') {
    editingAppId.value = null
    statusMessage.value = ''
  }
})

onMounted(fetchDashboard)
</script>