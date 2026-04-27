<template>
  <div class="app-container d-flex flex-column min-vh-100 bg-light">

    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm" v-if="showNav">
      <div class="container-fluid px-3">
        <router-link to="/" class="navbar-brand fw-bold text-white">
          FirstPlace
        </router-link>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">

          <ul class="navbar-nav me-auto gap-1">
            <li class="nav-item" v-if="user?.role === 'admin'">
              <router-link to="/admin" class="nav-link">Admin</router-link>
            </li>
            <li class="nav-item" v-if="user?.role === 'company'">
              <router-link to="/company" class="nav-link">Company</router-link>
            </li>
            <li class="nav-item" v-if="user?.role === 'student'">
              <router-link to="/student" class="nav-link">Student</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/chatbot" class="nav-link">Chatbot</router-link>
            </li>
          </ul>

          <ul class="navbar-nav align-items-center gap-2">
            <li class="nav-item" v-if="!user">
              <router-link to="/login" class="btn btn-outline-light btn-sm">Login</router-link>
            </li>
            <li class="nav-item" v-if="!user">
              <router-link to="/register" class="btn btn-light btn-sm">Register</router-link>
            </li>
            <li class="nav-item" v-if="user">
              <button class="btn btn-danger btn-sm" type="button" @click="logout">Logout</button>
            </li>
          </ul>

        </div>
      </div>
    </nav>

    <main class="flex-grow-1 container py-4">
      <router-view></router-view>
    </main>

    <footer class="text-center py-3 border-top bg-white small text-muted" v-if="showNav">
      FirstPlace · Campus hiring
    </footer>

    <LlmChatbot />

  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from './api'
import LlmChatbot from './views/LlmChatbot.vue'

export default {
  setup() {
    const router = useRouter()
    const route = useRoute()
    const user = ref(null)

    const showNav = computed(() => !['login', 'register'].includes(route.name))

    const loadUser = async () => {
      try {
        const res = await api.get('/auth/me')
        user.value = res.data
      } catch {
        user.value = null
      }
    }

    const logout = async () => {
      try {
        await api.post('/auth/logout')
      } catch (e) { }
      user.value = null
      router.push('/login')
    }

    onMounted(loadUser)
    router.afterEach(loadUser)

    return { user, showNav, logout }
  }
}
</script>
