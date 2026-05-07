<template>
  <div class="modal-overlay" v-if="visible" @click.self="close">
    <div class="login-card">
      <button class="close-btn" @click="close">&times;</button>

      <div class="login-header">
        <span class="login-icon">{{ isLogin ? '🔐' : '📝' }}</span>
        <h3>{{ isLogin ? '用户登录' : '注册账号' }}</h3>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" autocomplete="current-password" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '请稍候...' : (isLogin ? '登 录' : '注 册') }}
        </button>
      </form>

      <div class="switch-mode">
        <span v-if="isLogin">还没有账号？<a href="#" @click.prevent="isLogin = false">立即注册</a></span>
        <span v-else>已有账号？<a href="#" @click.prevent="isLogin = true">去登录</a></span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'LoginModal',
  props: {
    visible: { type: Boolean, default: false },
  },
  data() {
    return {
      isLogin: true,
      form: { username: '', password: '' },
      loading: false,
      error: '',
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.form = { username: '', password: '' }
        this.error = ''
        this.isLogin = true
      }
    },
  },
  methods: {
    close() {
      this.$emit('close')
    },
    async submit() {
      if (!this.form.username.trim() || !this.form.password.trim()) {
        this.error = '请填写用户名和密码'
        return
      }
      this.loading = true
      this.error = ''
      try {
        const url = this.isLogin ? '/login' : '/register'
        const { data } = await api.post(url, this.form)
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        this.$emit('success', data.user)
        this.close()
      } catch (err) {
        this.error = err.response?.data?.detail || '操作失败，请重试'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 20, 50, 0.5);
  backdrop-filter: blur(6px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  background: white;
  border-radius: 24px;
  padding: 35px 30px;
  width: 380px;
  max-width: 90vw;
  box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 14px;
  right: 16px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}
.close-btn:hover { color: #6366f1; }

.login-header {
  text-align: center;
  margin-bottom: 25px;
}

.login-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 8px;
}

.login-header h3 {
  font-size: 1.3rem;
  color: #1e293b;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 6px;
}

.field input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
  background: #f8fafc;
  box-sizing: border-box;
}

.field input:focus {
  border-color: #6366f1;
  background: white;
}

.error {
  color: #ef4444;
  font-size: 0.85rem;
  margin: 0;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-mode {
  text-align: center;
  margin-top: 18px;
  font-size: 0.88rem;
  color: #64748b;
}

.switch-mode a {
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
}

.switch-mode a:hover {
  text-decoration: underline;
}
</style>
