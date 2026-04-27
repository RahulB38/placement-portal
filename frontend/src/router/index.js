import { createRouter, createWebHistory } from 'vue-router'


const routes = [
  { path: '/', component: () => import('../views/Home.vue'), name: 'home' },
  { path: '/login', component: () => import('../views/Login.vue'), name: 'login' },
  { path: '/register', component: () => import('../views/Register.vue'), name: 'register' },
  { path: '/drives', component: () => import('../views/Drives.vue'), name: 'drives' },
  { path: '/drives/:id', component: () => import('../views/DriveDetail.vue'), name: 'drive-detail' },
  { path: '/admin', component: () => import('../views/admin/AdminDash.vue'), name: 'admin' },
  { path: '/company', component: () => import('../views/company/CompanyDash.vue'), name: 'company' },
  { path: '/student', component: () => import('../views/student/StudentDash.vue'), name: 'student' },
  { path: '/chatbot', component: () => import('../views/LlmChatbot.vue'), name: 'chatbot' }
]

const router = createRouter({ history: createWebHistory(), routes })
export default router
