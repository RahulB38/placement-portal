<template>
  <div class="container-fluid px-3 py-3">

    <h3 class="fw-bold text-primary mb-1">Admin summary</h3>
    <p class="text-muted mb-3 mb-md-4" v-if="welcomeLine">{{ welcomeLine }}</p>

    <div class="row g-4">
      <aside class="col-12 col-md-3 col-lg-2">
        <nav class="nav flex-column nav-pills dashboard-sidebar" aria-label="Admin sections">
          <a class="nav-link" :class="{ active: tab === 'overview' }" href="#"
            @click.prevent="tab = 'overview'">Overview</a>
          <a class="nav-link" :class="{ active: tab === 'companies' }" href="#"
            @click.prevent="tab = 'companies'">Companies</a>
          <a class="nav-link" :class="{ active: tab === 'students' }" href="#"
            @click.prevent="tab = 'students'">Students</a>
          <a class="nav-link" :class="{ active: tab === 'drives' }" href="#" @click.prevent="tab = 'drives'">Drives</a>
          <a class="nav-link" :class="{ active: tab === 'applications' }" href="#"
            @click.prevent="tab = 'applications'">Applications</a>
          <a class="nav-link" :class="{ active: tab === 'stats' }" href="#" @click.prevent="tab = 'stats'">Extra
            stats</a>
        </nav>
      </aside>
      <div class="col-12 col-md-9 col-lg-10 min-w-0">

        <div v-if="tab === 'overview'" class="card border shadow-sm">
          <div class="card-body">
            <h5 class="fw-semibold text-primary mb-4">Overview</h5>

            <h6 class="small fw-semibold text-secondary text-uppercase mb-3">Students</h6>
            <div class="row g-3 border-bottom pb-4 mb-4">
              <div class="col-6 col-md-3">
                <p class="small text-muted mb-1">Active students</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.total_students }}</p>
              </div>
              <div class="col-6 col-md-3">
                <p class="small text-muted mb-1">Registered (all)</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.registered_students }}</p>
              </div>
              <div class="col-6 col-md-3">
                <p class="small text-muted mb-1">Placed students</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.placed_students }}</p>
              </div>
              <div class="col-6 col-md-3">
                <p class="small text-muted mb-1">Blacklisted students</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.blacklisted_students }}</p>
              </div>
            </div>

            <h6 class="small fw-semibold text-secondary text-uppercase mb-3">Companies &amp; drives</h6>
            <div class="row g-3 border-bottom pb-4 mb-4">
              <div class="col-md-3">
                <p class="small text-muted mb-1">Approved companies</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.total_companies }}</p>
              </div>
              <div class="col-md-3">
                <p class="small text-muted mb-1">Pending companies</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.pending_companies }}</p>
              </div>
              <div class="col-md-3">
                <p class="small text-muted mb-1">Approved drives</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.total_drives }}</p>
              </div>
              <div class="col-md-3">
                <p class="small text-muted mb-1">Pending drives</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.pending_drives }}</p>
              </div>
            </div>

            <h6 class="small fw-semibold text-secondary text-uppercase mb-3">Applications</h6>
            <div class="row g-3 border-bottom pb-4 mb-4">
              <div class="col-md-4">
                <p class="small text-muted mb-1">Total applications</p>
                <p class="fs-4 fw-bold mb-0">{{ stats.total_applications }}</p>
              </div>
            </div>

            <h6 class="small fw-semibold text-secondary text-uppercase mb-3">Recent applications (sample)</h6>
            <div v-if="!stats.recent_applications?.length" class="text-muted small mb-0">No recent applications to show.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-sm table-bordered align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Student</th>
                    <th>Company</th>
                    <th>Drive</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(r, i) in stats.recent_applications" :key="i">
                    <td>{{ r.student_name }} <span class="text-muted small">({{ r.roll_number }})</span></td>
                    <td>{{ r.company_name }}</td>
                    <td>{{ r.drive_title }}</td>
                    <td><span class="badge bg-secondary">{{ r.status }}</span></td>
                    <td>{{ formatDate(r.application_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="tab === 'companies'" class="card border shadow-sm">
          <div class="card-body">
            <input type="text" class="form-control mb-3" placeholder="Search companies..." v-model="companySearch"
              @input="fetchCompanies" style="max-width: 320px;" />
            <div class="table-responsive">
              <table class="table table-bordered align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Company</th>
                    <th>HR</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="c in companies" :key="c.id">
                    <td>{{ c.company_name }}</td>
                    <td>{{ c.hr_contact }}</td>
                    <td>
                      <span class="badge"
                        :class="c.status === 'approved' ? 'bg-success' : c.status === 'pending' ? 'bg-warning text-dark' : c.status === 'blacklisted' ? 'bg-dark' : 'bg-danger'">{{
                        c.status }}</span>
                    </td>
                    <td>
                      <button v-if="c.status === 'pending'" class="btn btn-sm btn-primary me-1"
                        @click="approveCompany(c.id, true)">Approve</button>
                      <button v-if="c.status === 'pending'" class="btn btn-sm btn-outline-danger me-1"
                        @click="approveCompany(c.id, false)">Reject</button>
                      <button v-if="c.status === 'approved'" class="btn btn-sm btn-outline-secondary"
                        @click="deactivateCompany(c.id)">Blacklist company</button>
                      <button v-if="c.status === 'blacklisted'" class="btn btn-sm btn-success"
                        @click="deactivateCompany(c.id)">Reactivate company</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="tab === 'students'" class="card border shadow-sm">
          <div class="card-body">
            <input type="text" class="form-control mb-3" placeholder="Search students..." v-model="studentSearch"
              @input="fetchStudents" style="max-width: 320px;" />
            <div class="table-responsive">
              <table class="table table-bordered align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Name</th>
                    <th>Roll</th>
                    <th>Branch</th>
                    <th>CGPA</th>
                    <th>Flag</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in students" :key="s.id">
                    <td>{{ s.name }}</td>
                    <td>{{ s.roll_number }}</td>
                    <td>{{ s.branch }}</td>
                    <td>{{ s.cgpa }}</td>
                    <td>
                      <span v-if="s.is_blacklisted" class="badge bg-dark">Deactivated</span>
                      <span v-else class="badge bg-success">Active</span>
                    </td>
                    <td>
                      <button class="btn btn-sm" :class="s.is_blacklisted ? 'btn-success' : 'btn-outline-danger'"
                        @click="blacklistStudent(s.user_id)">
                        {{ s.is_blacklisted ? 'Reactivate student' : 'Deactivate student' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="tab === 'drives'" class="card border shadow-sm">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-bordered align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Job</th>
                    <th>Company</th>
                    <th>Status</th>
                    <th>Applicants</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="d in adminDrives" :key="d.id">
                    <td>{{ d.job_title }}</td>
                    <td>{{ d.company_name }}</td>
                    <td>
                      <span class="badge"
                        :class="d.status === 'approved' ? 'bg-success' : d.status === 'pending' ? 'bg-warning text-dark' : 'bg-secondary'">{{
                        d.status }}</span>
                    </td>
                    <td>{{ d.applicants_count }}</td>
                    <td>
                      <button v-if="d.status === 'pending'" class="btn btn-sm btn-primary me-1"
                        @click="approveDrive(d.id, true)">Approve</button>
                      <button v-if="d.status === 'pending'" class="btn btn-sm btn-outline-danger"
                        @click="approveDrive(d.id, false)">Reject</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="tab === 'applications'" class="card border shadow-sm">
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-bordered align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Student</th>
                    <th>Drive</th>
                    <th>Company</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in applications" :key="a.id">
                    <td>{{ a.student_name }} ({{ a.roll_number }})</td>
                    <td>{{ a.drive_title }}</td>
                    <td>{{ a.company_name }}</td>
                    <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
                    <td>{{ formatDate(a.application_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="tab === 'stats'" class="card border shadow-sm">
          <div class="card-body">
            <h6 class="fw-semibold mb-3">Placement overview</h6>
            <p>Total approved drives: <strong>{{ reportStats.total_drives }}</strong></p>
            <p>Total applications: <strong>{{ reportStats.total_applications }}</strong></p>
            <p>Selected rows: <strong>{{ reportStats.selected_count }}</strong></p>
            <p>Unique placed students: <strong>{{ reportStats.students_placed }}</strong></p>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../../api'

const tab = ref('overview')
const stats = ref({
  total_students: 0,
  registered_students: 0,
  placed_students: 0,
  blacklisted_students: 0,
  total_companies: 0,
  total_drives: 0,
  total_applications: 0,
  pending_companies: 0,
  pending_drives: 0,
  recent_applications: []
})
const companies = ref([])
const students = ref([])
const adminDrives = ref([])
const applications = ref([])
const reportStats = ref({})
const companySearch = ref('')
const studentSearch = ref('')
const welcomeLine = ref('')

const fetchStats = async () => {
  const r = await api.get('/admin/dashboard')
  stats.value = r.data
}

const fetchCompanies = () => api.get('/admin/companies', { params: { search: companySearch.value } }).then(r => { companies.value = r.data })
const fetchStudents = () => api.get('/admin/students', { params: { search: studentSearch.value } }).then(r => { students.value = r.data })
const fetchDrives = () => api.get('/admin/drives').then(r => { adminDrives.value = r.data })
const fetchApplications = () => api.get('/admin/applications').then(r => { applications.value = r.data })
const fetchReportStats = () => api.get('/admin/statistics').then(r => { reportStats.value = r.data })

const approveCompany = (id, approve) => api.post(`/admin/companies/${id}/approve`, { action: approve ? 'approve' : 'reject' }).then(() => { fetchCompanies(); fetchStats() })
const deactivateCompany = (id) => api.post(`/admin/companies/${id}/deactivate`).then(() => { fetchCompanies(); fetchStats() })
const blacklistStudent = (userId) => api.post(`/admin/students/${userId}/blacklist`).then(() => { fetchStudents(); fetchStats() })
const approveDrive = (id, approve) => api.post(`/admin/drives/${id}/approve`, { action: approve ? 'approve' : 'reject' }).then(() => { fetchDrives(); fetchStats() })

const statusBadge = (s) => {
  if (s === 'selected') return 'bg-success'
  if (s === 'shortlisted') return 'bg-info'
  if (s === 'rejected') return 'bg-danger'
  return 'bg-secondary'
}
const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '-'

watch(tab, t => {
  if (t === 'overview') fetchStats()
  if (t === 'companies') fetchCompanies()
  if (t === 'students') fetchStudents()
  if (t === 'drives') fetchDrives()
  if (t === 'applications') fetchApplications()
  if (t === 'stats') fetchReportStats()
})

onMounted(async () => {
  try {
    const me = await api.get('/auth/me')
    const w = me.data.welcome_name || me.data.email
    welcomeLine.value = w ? `Welcome ${w}` : ''
  } catch {
    welcomeLine.value = ''
  }
  await fetchStats()
})
</script>
