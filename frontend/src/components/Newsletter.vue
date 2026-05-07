<template>
  <section class="newsletter">
    <h2>📬 订阅旅行资讯</h2>
    <p>获取最新旅行攻略、特价机票和独家优惠</p>
    <form class="newsletter-form" @submit.prevent="handleSubmit">
      <input
        type="email"
        v-model="email"
        placeholder="输入您的邮箱地址"
        required
      >
      <button type="submit" :disabled="subscribing">{{ subscribing ? '提交中...' : '立即订阅' }}</button>
    </form>
  </section>
</template>

<script>
import api from '../api'

export default {
  name: 'Newsletter',
  inject: ['getUser', 'requestLogin'],
  data() {
    return {
      email: '',
      subscribing: false
    }
  },
  methods: {
    async handleSubmit() {
      if (!this.getUser()) {
        alert('请先登录后再订阅')
        this.requestLogin()
        return
      }
      if (!this.email.trim()) return
      this.subscribing = true
      try {
        const { data } = await api.post('/newsletter/subscribe', { email: this.email })
        alert(data.message || '订阅成功！')
        this.email = ''
      } catch (err) {
        const msg = err.response?.data?.detail || '订阅失败，请稍后重试'
        alert(msg)
      } finally {
        this.subscribing = false
      }
    }
  }
}
</script>

<style scoped>
.newsletter {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  padding: 80px 20px;
  text-align: center;
}

.newsletter h2 {
  color: white;
  font-size: 2.2rem;
  margin-bottom: 15px;
}

.newsletter p {
  color: rgba(255,255,255,0.9);
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.newsletter-form {
  display: flex;
  justify-content: center;
  gap: 15px;
  max-width: 500px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.newsletter-form input {
  flex: 1;
  min-width: 280px;
  padding: 16px 24px;
  border: none;
  border-radius: 14px;
  font-size: 1rem;
}

.newsletter-form button {
  background: white;
  color: var(--primary);
  border: none;
  padding: 16px 35px;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.newsletter-form button:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

@media (max-width: 768px) {
  .newsletter-form {
    flex-direction: column;
  }
  .newsletter-form input,
  .newsletter-form button {
    width: 100%;
  }
}
</style>