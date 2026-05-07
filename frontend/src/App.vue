<template>
  <div id="app">
    <AnimatedBackground />

    <!-- 顶部用户栏 -->
    <div class="user-bar">
      <template v-if="currentUser">
        <span class="user-info">
          <span class="user-avatar">{{ currentUser.username[0].toUpperCase() }}</span>
          {{ currentUser.username }}
          <span v-if="currentUser.role === 'admin'" class="admin-badge">管理员</span>
        </span>
        <button class="bar-btn my-bookings-btn" @click="showMyBookings = !showMyBookings">
          {{ showMyBookings ? '收起' : '我的预订' }}
        </button>
        <button v-if="currentUser.role === 'admin'" class="bar-btn admin-btn" @click="showAdmin = !showAdmin">
          {{ showAdmin ? '收起后台' : '管理后台' }}
        </button>
        <button class="bar-btn logout-btn" @click="logout">退出</button>
      </template>
      <template v-else>
        <button class="bar-btn login-btn" @click="showLogin = true">登录 / 注册</button>
      </template>
    </div>

    <!-- 我的预订面板 -->
    <transition name="slide-down">
      <div v-if="showMyBookings && currentUser" class="my-bookings-panel">
        <h3>我的预订</h3>
        <div class="admin-table-wrap">
          <table v-if="myBookings.length">
            <thead><tr><th>编号</th><th>目的地</th><th>姓名</th><th>手机</th><th>日期</th><th>人数</th><th>状态</th><th>时间</th></tr></thead>
            <tbody><tr v-for="b in myBookings" :key="b.id">
              <td>{{ b.id }}</td><td>{{ b.dest }}</td><td>{{ b.name }}</td><td>{{ b.phone }}</td>
              <td>{{ b.date }}</td><td>{{ b.people }}</td><td>{{ b.status }}</td><td>{{ b.created_at }}</td>
            </tr></tbody>
          </table>
          <p v-else class="empty">暂无预订记录</p>
        </div>
      </div>
    </transition>

    <!-- 管理后台面板 -->
    <transition name="slide-down">
      <div v-if="showAdmin && currentUser?.role === 'admin'" class="admin-panel">
        <h3>管理后台</h3>
        <div class="admin-tabs">
          <button :class="{ active: adminTab === 'bookings' }" @click="adminTab = 'bookings'">预约列表</button>
          <button :class="{ active: adminTab === 'users' }" @click="adminTab = 'users'">用户列表</button>
          <button :class="{ active: adminTab === 'subscribers' }" @click="adminTab = 'subscribers'">订阅列表</button>
        </div>

        <div v-if="adminTab === 'bookings'" class="admin-table-wrap">
          <table v-if="adminData.bookings?.length">
            <thead><tr><th>编号</th><th>目的地</th><th>姓名</th><th>手机</th><th>日期</th><th>人数</th><th>套餐</th><th>时间</th></tr></thead>
            <tbody><tr v-for="b in adminData.bookings" :key="b.id">
              <td>{{ b.id }}</td><td>{{ b.dest }}</td><td>{{ b.name }}</td><td>{{ b.phone }}</td>
              <td>{{ b.date }}</td><td>{{ b.people }}</td><td>{{ b.package || '-' }}</td><td>{{ b.created_at }}</td>
            </tr></tbody>
          </table>
          <p v-else class="empty">暂无预约记录</p>
        </div>

        <div v-if="adminTab === 'users'" class="admin-table-wrap">
          <table v-if="adminData.users?.length">
            <thead><tr><th>ID</th><th>用户名</th><th>角色</th><th>注册时间</th></tr></thead>
            <tbody><tr v-for="u in adminData.users" :key="u.id">
              <td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.role }}</td><td>{{ u.created_at }}</td>
            </tr></tbody>
          </table>
          <p v-else class="empty">暂无用户</p>
        </div>

        <div v-if="adminTab === 'subscribers'" class="admin-table-wrap">
          <table v-if="adminData.subscribers?.length">
            <thead><tr><th>ID</th><th>邮箱</th><th>订阅时间</th></tr></thead>
            <tbody><tr v-for="s in adminData.subscribers" :key="s.id">
              <td>{{ s.id }}</td><td>{{ s.email }}</td><td>{{ s.subscribed_at }}</td>
            </tr></tbody>
          </table>
          <p v-else class="empty">暂无订阅</p>
        </div>
      </div>
    </transition>

    <LoginModal :visible="showLogin" @close="showLogin = false" @success="onLogin" />

    <HeroSection />
    <SearchSection />
    <MysteryBox />
    <Destinations />
    <Checklist />
    <TipsSection />
    <Newsletter />
    <Footer />
  </div>
</template>

<script>
import AnimatedBackground from './components/AnimatedBackground.vue'
import HeroSection from './components/HeroSection.vue'
import SearchSection from './components/SearchSection.vue'
import MysteryBox from './components/MysteryBox.vue'
import Destinations from './components/Destinations.vue'
import Checklist from './components/Checklist.vue'
import TipsSection from './components/TipsSection.vue'
import Newsletter from './components/Newsletter.vue'
import Footer from './components/Footer.vue'
import LoginModal from './components/LoginModal.vue'
import api from './api'

export default {
  name: 'App',
  components: {
    AnimatedBackground, HeroSection, SearchSection, MysteryBox,
    Destinations, Checklist, TipsSection, Newsletter, Footer, LoginModal,
  },
  data() {
    return {
      currentUser: null,
      showLogin: false,
      showAdmin: false,
      showMyBookings: false,
      adminTab: 'bookings',
      adminData: { bookings: [], users: [], subscribers: [] },
      myBookings: [],
    }
  },
  provide() {
    return {
      getUser: () => this.currentUser,
      requestLogin: () => { this.showLogin = true },
    }
  },
  mounted() {
    const saved = localStorage.getItem('user')
    if (saved) {
      try { this.currentUser = JSON.parse(saved) } catch { /* ignore */ }
    }
  },
  watch: {
    showAdmin(val) {
      if (val) this.loadAdmin()
    },
    adminTab() {
      this.loadAdmin()
    },
    showMyBookings(val) {
      if (val) this.loadMyBookings()
    },
  },
  methods: {
    onLogin(user) {
      this.currentUser = user
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.currentUser = null
      this.showAdmin = false
      this.showMyBookings = false
    },
    async loadMyBookings() {
      try {
        const { data } = await api.get('/bookings')
        this.myBookings = data.bookings || []
      } catch {
        this.myBookings = []
      }
    },
    async loadAdmin() {
      try {
        const map = { bookings: '/admin/bookings', users: '/admin/users', subscribers: '/admin/subscribers' }
        const key = this.adminTab
        const { data } = await api.get(map[key])
        this.adminData[key] = data[key] || []
      } catch {
        this.adminData[this.adminTab] = []
      }
    },
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --secondary: #ec4899;
  --accent: #f59e0b;
  --success: #10b981;
  --dark: #1e293b;
  --light: #f8fafc;
}

body {
  font-family: 'Noto Sans SC', 'Segoe UI', sans-serif;
  background: var(--light);
  min-height: 100vh;
  color: #333;
  overflow-x: hidden;
}

.animate-on-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.animate-on-scroll.visible {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 768px) {
  .hero h1 { font-size: 2.2rem; }
  .hero-logo { font-size: 3.5rem; }
}
</style>

<style scoped>
.user-bar {
  position: fixed;
  top: 15px;
  right: 20px;
  z-index: 1500;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 30px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.admin-badge {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.72rem;
  font-weight: 600;
}

.bar-btn {
  padding: 8px 18px;
  border: none;
  border-radius: 30px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  color: #6366f1;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.login-btn:hover {
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99,102,241,0.3);
}

.my-bookings-btn {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.my-bookings-btn:hover { background: #10b981; color: white; }

.admin-btn {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  box-shadow: 0 4px 12px rgba(245,158,11,0.3);
}
.admin-btn:hover { transform: translateY(-2px); }

.logout-btn {
  background: rgba(255,255,255,0.95);
  color: #64748b;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.logout-btn:hover { color: #ef4444; }

/* My Bookings Panel */
.my-bookings-panel {
  position: fixed;
  top: 60px;
  right: 20px;
  width: 700px;
  max-width: calc(100vw - 40px);
  max-height: 50vh;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  z-index: 1400;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.my-bookings-panel h3 {
  padding: 18px 24px;
  font-size: 1.1rem;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}

/* Admin Panel */
.admin-panel {
  position: fixed;
  top: 60px;
  right: 20px;
  width: 700px;
  max-width: calc(100vw - 40px);
  max-height: 70vh;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  z-index: 1400;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.admin-panel h3 {
  padding: 18px 24px;
  font-size: 1.1rem;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}

.admin-tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #f1f5f9;
}

.admin-tabs button {
  flex: 1;
  padding: 12px;
  background: none;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.admin-tabs button.active {
  color: #6366f1;
  border-bottom-color: #6366f1;
}

.admin-tabs button:hover { color: #6366f1; }

.admin-table-wrap {
  overflow: auto;
  flex: 1;
  padding: 16px;
}

.admin-table-wrap table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.admin-table-wrap th {
  text-align: left;
  padding: 10px 8px;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  border-bottom: 2px solid #e2e8f0;
  white-space: nowrap;
}

.admin-table-wrap td {
  padding: 10px 8px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 40px;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

@media (max-width: 768px) {
  .user-bar {
    top: 10px;
    right: 10px;
  }
  .admin-panel,
  .my-bookings-panel {
    right: 10px;
    width: calc(100vw - 20px);
  }
}
</style>