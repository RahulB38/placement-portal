<template>
  <div class="container-fluid px-3 py-3">

    <h3 class="fw-bold text-primary mb-1" v-if="student">Welcome {{ student.name }}</h3>
    <p class="text-muted small mb-3 mb-md-4" v-if="student">{{ student.roll_number }} · {{ student.branch }} · Year {{ student.year }} · CGPA {{ student.cgpa }}</p>

    <div class="row g-4">
      <aside class="col-12 col-md-3 col-lg-2">
        <nav class="nav flex-column nav-pills dashboard-sidebar" aria-label="Student sections">
          <a class="nav-link" :class="{ active: tab === 'drives' }" href="#" @click.prevent="tab = 'drives'">Open drives</a>
          <a class="nav-link" :class="{ active: tab === 'applications' }" href="#" @click.prevent="tab = 'applications'">My applications</a>
          <a class="nav-link" :class="{ active: tab === 'profile' }" href="#" @click.prevent="tab = 'profile'">Profile</a>
        </nav>
      </aside>
      <div class="col-12 col-md-9 col-lg-10 min-w-0">

    <div v-if="tab === 'drives'" class="card border shadow-sm">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-12 col-md-6" v-for="d in drives" :key="d.id">
            <div class="card h-100 border-0 shadow-sm rounded-3 bg-light">
              <div class="card-body d-flex flex-column">
                <h6 class="fw-semibold mb-2">{{ d.job_title }}</h6>
                <p class="small text-muted mb-2">{{ d.company_name }}</p>
                <p class="small text-secondary mb-2">Deadline: {{ formatDate(d.deadline) }}</p>
                <span v-if="d.company_blacklisted" class="badge bg-dark mb-2 align-self-start">Company blacklisted</span>
                <div class="mt-auto d-flex gap-2">
                  <button type="button" class="btn btn-sm btn-outline-primary flex-fill" @click="openDriveDetail(d)">View</button>
                  <button v-if="d.applied" class="btn btn-sm btn-secondary flex-fill" disabled>Applied</button>
                  <button v-else-if="!d.eligible" class="btn btn-sm btn-outline-secondary flex-fill" disabled :title="d.eligibility_reason || ''">Not eligible</button>
                  <button v-else class="btn btn-sm btn-primary flex-fill" @click="apply(d.id)">Apply</button>
                </div>
                <p v-if="!d.eligible && d.eligibility_reason" class="small text-danger mt-2 mb-0">{{ d.eligibility_reason }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="tab === 'applications'" class="card border shadow-sm">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <h6 class="fw-semibold mb-0">History</h6>
          <button class="btn btn-primary btn-sm" @click="exportCsv" :disabled="exportLoading">{{ exportLoading ? 'Working...' : 'CSV export' }}</button>
        </div>
        <div class="table-responsive">
          <table class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Company</th>
                <th>Role</th>
                <th>Company flag</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in applications" :key="a.id">
                <td>{{ a.company_name }}</td>
                <td>{{ a.job_title }}</td>
                <td>
                  <span v-if="a.company_blacklisted" class="badge bg-dark">Blacklisted</span>
                  <span v-else class="badge bg-light text-dark border">Normal</span>
                </td>
                <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
                <td>{{ formatDate(a.application_date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="tab === 'profile'">
      <div v-if="profileSuccess" class="alert alert-success">
        <p class="mb-0 small">{{ profileSuccess }}</p>
      </div>
      <div v-if="profileError" class="alert alert-danger">
        <h6 class="alert-heading fw-bold small mb-1">Profile save issue</h6>
        <p class="mb-0 small">{{ profileError }}</p>
      </div>

      <div v-if="profileSummary" class="card border shadow-sm mb-3">
        <div class="card-body">
          <h6 class="fw-semibold text-primary mb-3">Your profile</h6>
          <dl class="row mb-0 small">
            <dt class="col-sm-3 col-md-2 text-muted">Name</dt>
            <dd class="col-sm-9 col-md-4">{{ profileSummary.name }}</dd>
            <dt class="col-sm-3 col-md-2 text-muted">Roll no.</dt>
            <dd class="col-sm-9 col-md-4">{{ profileSummary.roll_number }}</dd>
            <dt class="col-sm-3 col-md-2 text-muted">Branch</dt>
            <dd class="col-sm-9 col-md-4">{{ profileSummary.branch }}</dd>
            <dt class="col-sm-3 col-md-2 text-muted">Year</dt>
            <dd class="col-sm-9 col-md-4">{{ profileSummary.year }}</dd>
            <dt class="col-sm-3 col-md-2 text-muted">CGPA</dt>
            <dd class="col-sm-9 col-md-4">{{ profileSummary.cgpa }}</dd>
            <dt class="col-sm-3 col-md-2 text-muted">Phone</dt>
            <dd class="col-sm-9 col-md-4">{{ profileSummary.phone || '—' }}</dd>
          </dl>

          <div class="border-top pt-3 mt-3">
            <h6 class="small fw-semibold text-secondary text-uppercase mb-2">Resume (PDF only)</h6>
            <input
              ref="resumeFileInputRef"
              type="file"
              class="d-none"
              accept="application/pdf,.pdf"
              @change="onResumeFileSelected"
            />
            <div v-if="resumeUploadError" class="alert alert-danger py-2 small mb-2">{{ resumeUploadError }}</div>
            <div class="d-flex flex-wrap align-items-center gap-2">
              <template v-if="profileSummary.has_resume">
                <a
                  class="btn btn-outline-primary btn-sm"
                  href="/api/student/resume"
                  target="_blank"
                  rel="noopener noreferrer"
                >View resume</a>
                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  :disabled="resumeUploading"
                  @click="triggerResumePick"
                >{{ resumeUploading ? 'Uploading…' : 'Re-upload PDF' }}</button>
              </template>
              <template v-else>
                <button
                  type="button"
                  class="btn btn-outline-primary btn-sm"
                  :disabled="resumeUploading"
                  @click="triggerResumePick"
                >{{ resumeUploading ? 'Uploading…' : 'Upload resume (PDF)' }}</button>
              </template>
            </div>
          </div>

          <button
            v-if="!showProfileEdit"
            type="button"
            class="btn btn-primary mt-3"
            @click="openProfileEdit"
          >
            Update profile
          </button>
        </div>
      </div>

      <div v-if="showProfileEdit" class="card border shadow-sm">
        <div class="card-body">
          <h6 class="fw-semibold mb-3">Edit your details</h6>
          <form @submit.prevent="updateProfile">
            <div class="d-flex flex-column flex-xl-row flex-wrap gap-3 align-items-stretch align-items-xl-end mb-3">
              <div class="flex-fill" style="min-width: 11rem">
                <label class="form-label small mb-1">Full name</label>
                <input type="text" class="form-control" v-model="profileForm.name" required />
              </div>
              <div class="flex-fill" style="min-width: 9rem">
                <label class="form-label small mb-1">Branch</label>
                <select class="form-select" v-model="profileForm.branch" required>
                  <option value="" disabled>Select branch</option>
                  <option v-for="b in branchOptionsWithCurrent" :key="b" :value="b">{{ b }}</option>
                </select>
              </div>
              <div class="flex-fill" style="min-width: 6rem">
                <label class="form-label small mb-1">Year</label>
                <select class="form-select" v-model.number="profileForm.year" required>
                  <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                </select>
              </div>
              <div class="flex-fill" style="min-width: 7rem">
                <label class="form-label small mb-1">CGPA</label>
                <input type="number" step="0.01" class="form-control" v-model="profileForm.cgpa" min="0" max="10" required />
              </div>
              <div class="flex-fill" style="min-width: 10rem">
                <label class="form-label small mb-1">Phone (10 digits)</label>
                <input type="text" class="form-control" v-model="profileForm.phone" maxlength="10" pattern="[0-9]{10}" title="10 digits only" />
              </div>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <button type="submit" class="btn btn-primary">Save changes</button>
              <button type="button" class="btn btn-outline-secondary" @click="cancelProfileEdit">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>

      </div>
    </div>

    <div ref="driveDetailModalRef" class="modal fade" id="studentDriveDetailModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-scrollable modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title mb-0">{{ driveDetail?.job_title }}</h5>
              <p class="text-muted small mb-0">{{ driveDetail?.company_name }}</p>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="driveDetail">
            <section class="mb-3">
              <h6 class="small fw-semibold text-secondary text-uppercase mb-2">Job description</h6>
              <p class="mb-0 small" style="white-space: pre-wrap;">{{ driveDetail.job_description?.trim() || 'No description provided.' }}</p>
            </section>
            <section class="mb-3">
              <h6 class="small fw-semibold text-secondary text-uppercase mb-2">Eligible branches</h6>
              <p class="mb-0 small">{{ formatCommaList(driveDetail.eligibility_branches) }}</p>
            </section>
            <section class="mb-3">
              <h6 class="small fw-semibold text-secondary text-uppercase mb-2">Eligible years</h6>
              <p class="mb-0 small">{{ formatCommaList(driveDetail.eligible_years) }}</p>
            </section>
            <section>
              <h6 class="small fw-semibold text-secondary text-uppercase mb-2">Package info</h6>
              <p class="mb-0 small">{{ driveDetail.package_info?.trim() || 'Not specified.' }}</p>
            </section>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { Modal } from 'bootstrap'
import api from '../../api'

const tab = ref('drives')
const student = ref(null)
const drives = ref([])
const applications = ref([])
const profileSummary = ref(null)
const showProfileEdit = ref(false)
const profileForm = ref({ name: '', branch: '', year: 3, cgpa: 0, phone: '' })
const branchOptions = ['CSE', 'IT', 'ECE', 'EEE', 'Mechanical', 'DS', 'AI', 'Robotics', 'Civil', 'Other']
const branchOptionsWithCurrent = computed(() => {
  const b = profileForm.value.branch
  if (b && !branchOptions.includes(b)) {
    return [...branchOptions, b]
  }
  return branchOptions
})
const yearOptions = [1, 2, 3, 4]
const exportLoading = ref(false)
const profileError = ref('')
const profileSuccess = ref('')
const driveDetailModalRef = ref(null)
const driveDetail = ref(null)
const resumeFileInputRef = ref(null)
const resumeUploading = ref(false)
const resumeUploadError = ref('')

const formatDate = (d) => d ? new Date(d).toLocaleDateString() : '-'
const formatCommaList = (raw) => {
  if (raw == null || String(raw).trim() === '') return 'Not specified'
  return String(raw)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .join(', ')
}

const openDriveDetail = async (d) => {
  driveDetail.value = d
  await nextTick()
  const el = driveDetailModalRef.value
  if (el) Modal.getOrCreateInstance(el).show()
}
const statusBadge = (s) => s === 'selected' ? 'bg-success' : s === 'shortlisted' ? 'bg-info' : s === 'rejected' ? 'bg-danger' : 'bg-secondary'

const fetchDashboard = async () => {
  const res = await api.get('/student/dashboard')
  student.value = res.data.student
  drives.value = res.data.drives
  applications.value = res.data.applications
}

const apply = async (driveId) => {
  try {
    await api.post(`/student/apply/${driveId}`)
    fetchDashboard()
  } catch (e) {
    window.alert(e.response?.data?.error || 'Apply failed')
  }
}

const syncProfileFromApi = (data) => {
  profileSummary.value = {
    name: data.name,
    roll_number: data.roll_number,
    branch: data.branch,
    year: data.year,
    cgpa: data.cgpa,
    phone: data.phone || '',
    has_resume: !!data.has_resume
  }
  profileForm.value = {
    name: data.name,
    branch: data.branch,
    year: data.year,
    cgpa: data.cgpa,
    phone: data.phone || ''
  }
}

const triggerResumePick = () => {
  resumeUploadError.value = ''
  resumeFileInputRef.value?.click()
}

const onResumeFileSelected = async (e) => {
  const input = e.target
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  resumeUploadError.value = ''
  const okType = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  if (!okType) {
    resumeUploadError.value = 'Please choose a PDF file.'
    return
  }
  resumeUploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    await api.post('/student/resume', fd)
    const res = await api.get('/student/profile')
    syncProfileFromApi(res.data)
    profileSuccess.value = 'Resume uploaded successfully.'
  } catch (err) {
    resumeUploadError.value = err.response?.data?.error || 'Upload failed'
  } finally {
    resumeUploading.value = false
  }
}

const openProfileEdit = () => {
  profileError.value = ''
  profileSuccess.value = ''
  resumeUploadError.value = ''
  if (profileSummary.value) {
    profileForm.value = {
      name: profileSummary.value.name,
      branch: profileSummary.value.branch,
      year: profileSummary.value.year,
      cgpa: profileSummary.value.cgpa,
      phone: profileSummary.value.phone || ''
    }
  }
  showProfileEdit.value = true
}

const cancelProfileEdit = () => {
  showProfileEdit.value = false
  profileError.value = ''
  if (profileSummary.value) {
    profileForm.value = {
      name: profileSummary.value.name,
      branch: profileSummary.value.branch,
      year: profileSummary.value.year,
      cgpa: profileSummary.value.cgpa,
      phone: profileSummary.value.phone || ''
    }
  }
}

const updateProfile = async () => {
  profileError.value = ''
  profileSuccess.value = ''
  try {
    await api.put('/student/profile', {
      name: profileForm.value.name,
      branch: profileForm.value.branch,
      year: parseInt(profileForm.value.year, 10),
      cgpa: parseFloat(profileForm.value.cgpa),
      phone: profileForm.value.phone
    })
    const res = await api.get('/student/profile')
    syncProfileFromApi(res.data)
    await fetchDashboard()
    showProfileEdit.value = false
    profileSuccess.value = 'Profile updated successfully.'
  } catch (e) {
    const msg = e.response?.data?.error || 'Could not save'
    profileError.value = /cgpa/i.test(msg) ? 'Invalid CGPA. Enter a value between 0 and 10.' : msg
  }
}

const exportCsv = async () => {
  exportLoading.value = true
  try {
    const res = await api.post('/student/export-csv')
    if (res.data.sync && res.data.result?.csv) {
      const r = res.data.result
      const blob = new Blob([r.csv], { type: 'text/csv' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = r.filename || 'applications.csv'
      a.click()
      exportLoading.value = false
      return
    }
    const taskId = res.data.task_id
    const check = async () => {
      const statusRes = await api.get(`/student/export-status/${taskId}`)
      if (statusRes.data.status === 'complete') {
        const r = statusRes.data.result
        if (r.csv) {
          const blob = new Blob([r.csv], { type: 'text/csv' })
          const a = document.createElement('a')
          a.href = URL.createObjectURL(blob)
          a.download = r.filename || 'applications.csv'
          a.click()
        }
        exportLoading.value = false
      } else if (statusRes.data.status === 'failed') {
        window.alert(statusRes.data.error || 'Export failed')
        exportLoading.value = false
      } else {
        setTimeout(check, 1000)
      }
    }
    setTimeout(check, 500)
  } catch (e) {
    exportLoading.value = false
    window.alert(e.response?.data?.error || 'Export failed')
  }
}

watch(tab, async (t) => {
  if (t === 'profile') {
    profileError.value = ''
    profileSuccess.value = ''
    resumeUploadError.value = ''
    showProfileEdit.value = false
    try {
      const res = await api.get('/student/profile')
      syncProfileFromApi(res.data)
    } catch {
      profileSummary.value = null
    }
  }
})

onMounted(fetchDashboard)
</script>
