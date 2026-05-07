<template>
  <div class="modal-overlay" v-if="visible" @click.self="close">
    <div class="modal-container" :class="{ show: visible }">
      <!-- 顶部轮播图 -->
      <div class="carousel-section">
        <div class="carousel-wrapper">
          <div class="carousel-slides" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
            <div v-for="(slide, index) in destination.carousel" :key="index" class="carousel-slide">
              <img :src="slide.url" :alt="slide.caption" />
              <div class="carousel-caption">{{ slide.caption }}</div>
            </div>
          </div>
          <div class="carousel-controls">
            <button class="carousel-btn prev" @click="prevSlide">&#10094;</button>
            <button class="carousel-btn next" @click="nextSlide">&#10095;</button>
          </div>
          <div class="carousel-indicators">
            <span v-for="(slide, index) in destination.carousel" :key="index"
              :class="{ active: currentSlide === index }"
              @click="currentSlide = index"></span>
          </div>
        </div>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <!-- 可滚动内容区域 -->
      <div class="modal-content" ref="contentRef">
        <!-- 目的地标题、标签 -->
        <div class="header-section">
          <h1 class="destination-title">{{ destination.name }}</h1>
          <div class="tags-row">
            <span class="region-tag">&#127759; {{ destination.region }}</span>
            <span class="rating-tag">&#11088; {{ destination.rating }}分</span>
            <span class="badge-tag" :style="{ background: gradientColor }">{{ destination.badge }}</span>
            <span class="heat-tag">&#128293; 热度 98%</span>
          </div>
        </div>

        <!-- 核心简介 -->
        <div class="intro-section">
          <h3 class="section-title">&#10024; 旅行简介</h3>
          <p class="intro-text">{{ destination.intro }}</p>
          <p class="highlight-text">{{ destination.highlights }}</p>
        </div>

        <!-- 必玩景点 -->
        <div class="attractions-section">
          <h3 class="section-title">&#127919; 必玩热门景点</h3>
          <div class="attractions-grid">
            <div v-for="attr in destination.attractions" :key="attr.name" class="attraction-card">
              <span class="attr-tag">{{ attr.tag }}</span>
              <h4>{{ attr.name }}</h4>
              <p>{{ attr.desc }}</p>
            </div>
          </div>
        </div>

        <!-- 网红美食 -->
        <div class="food-section">
          <h3 class="section-title">&#127836; 网红特色美食</h3>
          <div class="food-list">
            <div v-for="food in destination.foods" :key="food.name" class="food-item">
              <div class="food-info">
                <h4>{{ food.name }}</h4>
                <p>{{ food.desc }}</p>
              </div>
              <span class="food-price">{{ food.price }}</span>
            </div>
          </div>
        </div>

        <!-- 人文风俗 -->
        <div class="culture-section">
          <h3 class="section-title">&#127917; 人文风俗</h3>
          <p class="culture-text">{{ destination.culture }}</p>
        </div>

        <!-- 行程套餐 -->
        <div class="packages-section">
          <h3 class="section-title">&#128197; 精选游玩行程</h3>
          <div class="packages-grid">
            <div v-for="(pkg, index) in destination.packages" :key="index" class="package-card">
              <div class="package-header">
                <h4>{{ pkg.name }}</h4>
                <span class="package-duration">{{ pkg.duration }}</span>
              </div>
              <div class="package-highlight">{{ pkg.highlight }}</div>
              <div class="package-suitable">&#128101; {{ pkg.suitable }}</div>
              <div class="package-features">
                <span v-for="feat in pkg.features" :key="feat" class="feature-tag">{{ feat }}</span>
              </div>
              <div class="package-price-row">
                <span class="package-price">{{ pkg.price }}</span>
                <span class="package-includes">含: {{ pkg.includes }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 价格明细 -->
        <div class="price-detail-section">
          <h3 class="section-title">&#128176; 套餐价格明细</h3>
          <div class="price-grid">
            <div class="price-box">
              <h4>&#9989; 基础费用包含</h4>
              <ul>
                <li v-for="item in destination.priceDetail.base" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="price-box">
              <h4>&#9888;&#65039; 自费项目说明</h4>
              <ul>
                <li v-for="item in destination.priceDetail.extra" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="price-box">
              <h4>&#128104;&#8205;&#128105;&#8205;&#128102; 出行人数可选</h4>
              <ul>
                <li v-for="item in destination.priceDetail.people" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="price-box">
              <h4>&#127800; 最佳出行建议</h4>
              <ul>
                <li v-for="item in destination.priceDetail.seasons" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 避坑指南 -->
        <div class="tips-section">
          <h3 class="section-title">&#128161; 游玩避坑指南</h3>
          <div class="tips-list">
            <div v-for="(tip, index) in destination.tips" :key="index" class="tip-item">
              <span class="tip-num">{{ index + 1 }}</span>
              <p>{{ tip }}</p>
            </div>
          </div>
        </div>

        <!-- 穿搭建议 -->
        <div class="outfit-section">
          <h3 class="section-title">&#128087; 出行穿搭建议</h3>
          <div class="outfit-grid">
            <div class="outfit-card spring">
              <span class="outfit-icon">&#127793;</span>
              <h4>春季</h4>
              <p>{{ destination.outfit.spring }}</p>
            </div>
            <div class="outfit-card summer">
              <span class="outfit-icon">&#9728;&#65039;</span>
              <h4>夏季</h4>
              <p>{{ destination.outfit.summer }}</p>
            </div>
            <div class="outfit-card autumn">
              <span class="outfit-icon">&#127810;</span>
              <h4>秋季</h4>
              <p>{{ destination.outfit.autumn }}</p>
            </div>
            <div class="outfit-card winter">
              <span class="outfit-icon">&#10052;&#65039;</span>
              <h4>冬季</h4>
              <p>{{ destination.outfit.winter }}</p>
            </div>
          </div>
        </div>

        <!-- 小众打卡秘境 -->
        <div class="secrets-section">
          <h3 class="section-title">&#128302; 本地小众打卡秘境</h3>
          <div class="secrets-grid">
            <div v-for="secret in destination.secrets" :key="secret.name" class="secret-card">
              <h4>{{ secret.name }}</h4>
              <p>{{ secret.desc }}</p>
            </div>
          </div>
        </div>

        <!-- 底部功能按钮 -->
        <div class="action-section">
          <button class="action-btn consult" :class="{ active: showChat }" @click="toggleChat">
            <span>&#128172;</span> {{ showChat ? '收起客服' : '在线咨询客服' }}
          </button>
          <button class="action-btn book" @click="openBooking">
            <span>&#9992;&#65039;</span> 立即预约报名
          </button>
          <button class="action-btn favorite" :class="{ active: isFavorite }" @click="toggleFavorite">
            <span>{{ isFavorite ? '&#128150;' : '&#129773;' }}</span> {{ isFavorite ? '已收藏' : '收藏目的地' }}
          </button>
        </div>

        <!-- 嵌入式客服聊天面板 -->
        <transition name="chat-slide">
          <div v-if="showChat" class="chat-panel">
            <div class="chat-header">
              <span class="chat-header-icon">&#129302;</span>
              <div>
                <h4>智能旅行顾问</h4>
                <span class="chat-status">&#128994; 在线</span>
              </div>
            </div>
            <div class="chat-messages" ref="chatMessagesRef">
              <div v-for="(msg, i) in chatMessages" :key="i"
                :class="['chat-message', msg.role === 'user' ? 'user-msg' : 'bot-msg']">
                <div class="msg-bubble">{{ msg.text }}</div>
              </div>
              <div v-if="isTyping" class="chat-message bot-msg">
                <div class="msg-bubble typing">客服正在输入<span class="typing-dots">...</span></div>
              </div>
            </div>
            <div class="chat-quick-questions" v-if="chatMessages.length <= 1">
              <button v-for="q in quickQuestions" :key="q" class="quick-q-btn" @click="sendQuickQuestion(q)">{{ q }}</button>
            </div>
            <div class="chat-input-area">
              <input v-model="chatInput" @keyup.enter="sendMessage" placeholder="输入您的问题..." class="chat-input" />
              <button class="chat-send-btn" @click="sendMessage" :disabled="!chatInput.trim()">&#10148;</button>
            </div>
          </div>
        </transition>
      </div>

      <!-- 预约报名弹窗 -->
      <transition name="booking-fade">
        <div v-if="showBooking" class="booking-overlay" @click.self="closeBooking">
          <div class="booking-card" v-if="!bookingSubmitted">
            <button class="booking-close" @click="closeBooking">&times;</button>
            <h3 class="booking-title">&#9992;&#65039; 预约报名</h3>
            <p class="booking-dest">{{ destination.name }}旅行</p>
            <div class="booking-form">
              <div class="form-group">
                <label>姓名 <span class="required">*</span></label>
                <input v-model="bookingForm.name" placeholder="请输入您的姓名" />
                <span v-if="bookingErrors.name" class="form-error">{{ bookingErrors.name }}</span>
              </div>
              <div class="form-group">
                <label>手机号 <span class="required">*</span></label>
                <input v-model="bookingForm.phone" placeholder="请输入11位手机号" maxlength="11" />
                <span v-if="bookingErrors.phone" class="form-error">{{ bookingErrors.phone }}</span>
              </div>
              <div class="form-group">
                <label>出行日期 <span class="required">*</span></label>
                <input v-model="bookingForm.date" type="date" />
                <span v-if="bookingErrors.date" class="form-error">{{ bookingErrors.date }}</span>
              </div>
              <div class="form-group">
                <label>出行人数</label>
                <div class="number-picker">
                  <button @click="bookingForm.people > 1 && bookingForm.people--" :disabled="bookingForm.people <= 1">-</button>
                  <span class="number-value">{{ bookingForm.people }}人</span>
                  <button @click="bookingForm.people < 20 && bookingForm.people++" :disabled="bookingForm.people >= 20">+</button>
                </div>
              </div>
              <div class="form-group">
                <label>选择套餐</label>
                <select v-model="bookingForm.package">
                  <option v-for="pkg in destination.packages" :key="pkg.name" :value="pkg.name">
                    {{ pkg.name }} ({{ pkg.duration }}) - {{ pkg.price }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>备注</label>
                <textarea v-model="bookingForm.remark" placeholder="其他需求或备注（选填）" rows="2"></textarea>
              </div>
              <button class="booking-submit-btn" @click="submitBooking">提交预约</button>
            </div>
          </div>
          <div class="booking-card booking-success" v-else>
            <div class="success-icon">&#127881;</div>
            <h3>预约成功！</h3>
            <div class="success-info">
              <p><strong>目的地：</strong>{{ bookingInfo.dest }}</p>
              <p><strong>出行人：</strong>{{ bookingInfo.name }}</p>
              <p><strong>手机号：</strong>{{ bookingInfo.phone }}</p>
              <p><strong>出行日期：</strong>{{ bookingInfo.date }}</p>
              <p><strong>人数：</strong>{{ bookingInfo.people }}人</p>
              <p v-if="bookingInfo.package"><strong>套餐：</strong>{{ bookingInfo.package }}</p>
            </div>
            <p class="success-tip">客服将尽快联系您确认行程详情</p>
            <button class="booking-submit-btn" @click="closeBooking">好的</button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'DestinationModal',
  inject: ['getUser', 'requestLogin'],
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    destination: {
      type: Object,
      default: () => ({})
    },
    isFavorited: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      currentSlide: 0,
      isFavorite: false,
      gradientColor: 'linear-gradient(135deg, #6366f1, #ec4899)',
      // 聊天相关
      showChat: false,
      chatMessages: [],
      chatInput: '',
      isTyping: false,
      chatSessionId: '',
      quickQuestions: [],
      // 预约相关
      showBooking: false,
      bookingSubmitted: false,
      bookingForm: {
        name: '',
        phone: '',
        date: '',
        people: 2,
        package: '',
        remark: ''
      },
      bookingErrors: {},
      bookingInfo: {}
    }
  },
  watch: {
    visible(val) {
      if (val) {
        this.currentSlide = 0
        this.isFavorite = this.isFavorited
        if (this.destination.gradient) {
          this.gradientColor = this.destination.gradient
        }
        this.initChat()
        this.showBooking = false
        this.bookingSubmitted = false
        this.bookingForm = { name: '', phone: '', date: '', people: 2, package: '', remark: '' }
        this.bookingErrors = {}
      }
    },
    isFavorited(val) {
      this.isFavorite = val
    }
  },
  methods: {
    close() {
      this.showChat = false
      this.$emit('close')
    },
    prevSlide() {
      if (this.destination.carousel) {
        this.currentSlide = (this.currentSlide - 1 + this.destination.carousel.length) % this.destination.carousel.length
      }
    },
    nextSlide() {
      if (this.destination.carousel) {
        this.currentSlide = (this.currentSlide + 1) % this.destination.carousel.length
      }
    },
    toggleFavorite() {
      this.isFavorite = !this.isFavorite
      if (this.isFavorite) {
        this.$emit('favorite', this.destination)
      } else {
        this.$emit('unfavorite', this.destination)
      }
    },
    // ===== 客服聊天 =====
    initChat() {
      const name = this.destination.name || '目的地'
      this.chatMessages = []
      this.chatInput = ''
      this.isTyping = false
      this.chatSessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
      this.quickQuestions = [
        '推荐几日游？',
        '有什么美食？',
        '最佳出行季节？',
        '大概预算多少？'
      ]
      this.chatMessages.push({
        role: 'bot',
        text: `您好！我是${name}旅行顾问 &#128075; 有任何关于${name}旅行的问题都可以问我哦～`
      })
    },
    toggleChat() {
      this.showChat = !this.showChat
      if (this.showChat) {
        this.$nextTick(() => this.scrollChatToBottom())
      }
    },
    sendQuickQuestion(q) {
      this.chatInput = q
      this.sendMessage()
    },
    async sendMessage() {
      if (!this.getUser()) {
        alert('请先登录后再使用客服咨询')
        this.requestLogin()
        return
      }
      const text = this.chatInput.trim()
      if (!text) return
      this.chatMessages.push({ role: 'user', text })
      this.chatInput = ''
      this.$nextTick(() => this.scrollChatToBottom())
      this.isTyping = true
      try {
        const history = this.chatMessages.slice(0, -1).map(m => ({
          role: m.role === 'user' ? 'user' : 'bot',
          text: m.text,
        }))
        const { data } = await api.post('/chat', {
          destination: this.destination.name || '目的地',
          message: text,
          history,
          sessionId: this.chatSessionId,
        })
        this.isTyping = false
        this.chatMessages.push({ role: 'bot', text: data.reply })
        this.$nextTick(() => this.scrollChatToBottom())
      } catch {
        this.isTyping = false
        this.chatMessages.push({ role: 'bot', text: '抱歉，客服暂时无法回复，请稍后再试～' })
        this.$nextTick(() => this.scrollChatToBottom())
      }
    },
    generateReply(msg) {
      const d = this.destination
      const name = d.name || '目的地'
      if (/几日|行程|路线|推荐/.test(msg)) {
        const pkgs = (d.packages || []).map(p => `${p.name}(${p.duration})${p.price}，${p.highlight}`).join('；')
        return pkgs ? `为您推荐${name}的精选行程：${pkgs}。建议初次游玩选择3日经典环线游，性价比最高哦～` : `${name}有很多精彩行程，建议选择3日游体验最丰富！`
      }
      if (/美食|吃|小吃|餐厅/.test(msg)) {
        const foods = (d.foods || []).map(f => `${f.name}(${f.price})`).join('、')
        return foods ? `${name}必吃美食：${foods}。每一道都值得尝试！` : `${name}有很多特色美食，来了千万别错过！`
      }
      if (/季节|天气|什么时候|时间|出行/.test(msg)) {
        const seasons = (d.priceDetail && d.priceDetail.seasons) ? d.priceDetail.seasons.join('；') : ''
        return seasons ? `关于出行时间：${seasons}。记得提前查好天气哦～` : `${name}四季各有特色，春秋最佳！`
      }
      if (/预算|花费|价格|多少钱|费用/.test(msg)) {
        const base = d.priceDetail && d.priceDetail.base ? d.priceDetail.base.join('、') : ''
        const extra = d.priceDetail && d.priceDetail.extra ? d.priceDetail.extra.join('、') : ''
        return `${name}参考价格${d.price || ''}起，费用包含：${base}。额外费用：${extra}。实际花费因人而异～`
      }
      if (/景点|玩|去哪|打卡/.test(msg)) {
        const attrs = (d.attractions || []).slice(0, 4).map(a => a.name).join('、')
        return attrs ? `${name}必玩景点：${attrs}。每个都很有特色！` : `${name}有很多精彩景点等您探索！`
      }
      if (/穿|衣服|装备/.test(msg)) {
        const o = d.outfit || {}
        return `穿搭建议 - 春：${o.spring || ''}；夏：${o.summer || ''}；秋：${o.autumn || ''}；冬：${o.winter || ''}。建议根据出行季节准备～`
      }
      if (/注意|避坑|tip/.test(msg)) {
        const tips = (d.tips || []).join('；')
        return tips ? `游玩贴士：${tips}。提前做好准备，玩得更尽兴！` : '建议提前规划好行程，注意安全！'
      }
      return `感谢您的咨询！关于${name}旅行，您还可以问我：行程推荐、美食攻略、出行季节、费用预算、必玩景点等问题哦～`
    },
    scrollChatToBottom() {
      const el = this.$refs.chatMessagesRef
      if (el) el.scrollTop = el.scrollHeight
    },
    // ===== 预约报名 =====
    openBooking() {
      if (this.destination.packages && this.destination.packages.length) {
        this.bookingForm.package = this.destination.packages[0].name
      }
      this.showBooking = true
      this.bookingSubmitted = false
    },
    closeBooking() {
      this.showBooking = false
    },
    async submitBooking() {
      if (!this.getUser()) {
        alert('请先登录后再进行预约')
        this.requestLogin()
        return
      }
      this.bookingErrors = {}
      if (!this.bookingForm.name.trim()) {
        this.bookingErrors.name = '请输入姓名'
      }
      if (!this.bookingForm.phone.trim()) {
        this.bookingErrors.phone = '请输入手机号'
      } else if (!/^1[3-9]\d{9}$/.test(this.bookingForm.phone)) {
        this.bookingErrors.phone = '请输入正确的11位手机号'
      }
      if (!this.bookingForm.date) {
        this.bookingErrors.date = '请选择出行日期'
      }
      if (Object.keys(this.bookingErrors).length > 0) return
      try {
        await api.post('/booking', {
          dest: this.destination.name,
          name: this.bookingForm.name,
          phone: this.bookingForm.phone,
          date: this.bookingForm.date,
          people: this.bookingForm.people,
          package: this.bookingForm.package,
          remark: this.bookingForm.remark,
        })
        this.bookingInfo = {
          dest: this.destination.name,
          name: this.bookingForm.name,
          phone: this.bookingForm.phone,
          date: this.bookingForm.date,
          people: this.bookingForm.people,
          package: this.bookingForm.package
        }
        this.bookingSubmitted = true
      } catch (err) {
        const msg = err.response?.data?.detail || '预约失败，请稍后重试'
        alert(msg)
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 20, 50, 0.6);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  background: linear-gradient(180deg, #f8f6fc 0%, #ffffff 100%);
  border-radius: 28px 28px 0 0;
  overflow: hidden;
  transform: translateY(100%);
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 -20px 60px rgba(99, 102, 241, 0.3);
  position: relative;
}

.modal-container.show {
  transform: translateY(0);
}

.carousel-section {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.carousel-wrapper {
  position: relative;
  height: 100%;
}

.carousel-slides {
  display: flex;
  height: 100%;
  transition: transform 0.5s ease;
}

.carousel-slide {
  width: 100%;
  height: 100%;
  position: relative;
  flex-shrink: 0;
}

.carousel-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.carousel-slide::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60%;
  background: linear-gradient(to top, rgba(30, 20, 50, 0.8) 0%, transparent 100%);
}

.carousel-caption {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  text-shadow: 0 2px 10px rgba(0,0,0,0.5);
  z-index: 2;
}

.carousel-controls {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
  z-index: 3;
}

.carousel-btn {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.9);
  border: none;
  border-radius: 50%;
  color: #6366f1;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.carousel-btn:hover {
  background: white;
  transform: scale(1.1);
}

.carousel-indicators {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 3;
}

.carousel-indicators span {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.5);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.carousel-indicators span.active {
  background: white;
  width: 20px;
  border-radius: 4px;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.95);
  border: none;
  border-radius: 50%;
  color: #6366f1;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  transform: scale(1.1);
}

.modal-content {
  padding: 20px;
  max-height: calc(90vh - 220px);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.3) transparent;
}

.modal-content::-webkit-scrollbar {
  width: 4px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.3);
  border-radius: 2px;
}

.header-section {
  text-align: center;
  margin-bottom: 20px;
}

.destination-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.tags-row {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.region-tag, .rating-tag, .badge-tag, .heat-tag {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
  transition: all 0.3s;
}

.badge-tag {
  color: white;
}

.heat-tag {
  color: #ec4899;
  background: rgba(236, 72, 153, 0.1);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #4c1d95;
  margin-bottom: 15px;
  padding-left: 12px;
  position: relative;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  border-radius: 2px;
}

.intro-section {
  margin-bottom: 25px;
  padding: 15px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(236, 72, 153, 0.05));
  border-radius: 16px;
}

.intro-text {
  font-size: 0.95rem;
  color: #475569;
  line-height: 1.8;
  margin-bottom: 10px;
}

.highlight-text {
  font-size: 0.9rem;
  color: #6366f1;
  line-height: 1.7;
}

.attractions-section {
  margin-bottom: 25px;
}

.attractions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.attraction-card {
  background: white;
  padding: 12px;
  border-radius: 14px;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.1);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.attraction-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
}

.attraction-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
}

.attr-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  font-size: 0.75rem;
  border-radius: 12px;
}

.attraction-card h4 {
  font-size: 0.95rem;
  color: #1e293b;
  margin-bottom: 6px;
}

.attraction-card p {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.5;
}

.food-section {
  margin-bottom: 25px;
}

.food-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.food-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(99, 102, 241, 0.08);
  transition: all 0.3s;
}

.food-item:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(236, 72, 153, 0.05));
}

.food-info h4 {
  font-size: 0.9rem;
  color: #1e293b;
  margin-bottom: 4px;
}

.food-info p {
  font-size: 0.8rem;
  color: #64748b;
}

.food-price {
  font-size: 0.85rem;
  color: #ec4899;
  font-weight: 600;
  padding: 4px 10px;
  background: rgba(236, 72, 153, 0.1);
  border-radius: 10px;
}

.culture-section {
  margin-bottom: 25px;
  padding: 15px;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.08), rgba(236, 72, 153, 0.08));
  border-radius: 16px;
}

.culture-text {
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.8;
}

.packages-section {
  margin-bottom: 25px;
}

.packages-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.package-card {
  background: white;
  border-radius: 18px;
  padding: 15px;
  box-shadow: 0 5px 20px rgba(99, 102, 241, 0.12);
  border: 2px solid transparent;
  transition: all 0.3s;
}

.package-card:hover {
  border-color: rgba(99, 102, 241, 0.3);
  transform: scale(1.02);
}

.package-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.package-header h4 {
  font-size: 1rem;
  color: #4c1d95;
  font-weight: 600;
}

.package-duration {
  padding: 5px 12px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: white;
  font-size: 0.8rem;
  border-radius: 12px;
}

.package-highlight {
  font-size: 0.9rem;
  color: #6366f1;
  font-weight: 500;
  margin-bottom: 8px;
}

.package-suitable {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 10px;
}

.package-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.feature-tag {
  padding: 4px 10px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-size: 0.75rem;
  border-radius: 10px;
}

.package-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
}

.package-price {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ec4899;
}

.package-includes {
  font-size: 0.75rem;
  color: #94a3b8;
}

.price-detail-section {
  margin-bottom: 25px;
}

.price-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.price-box {
  background: white;
  padding: 12px;
  border-radius: 14px;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.08);
}

.price-box h4 {
  font-size: 0.85rem;
  color: #4c1d95;
  margin-bottom: 10px;
}

.price-box ul {
  list-style: none;
  padding: 0;
}

.price-box li {
  font-size: 0.8rem;
  color: #64748b;
  padding: 4px 0;
  position: relative;
  padding-left: 12px;
}

.price-box li::before {
  content: '\2022';
  position: absolute;
  left: 0;
  color: #6366f1;
}

.tips-section {
  margin-bottom: 25px;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(99, 102, 241, 0.08);
}

.tip-num {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  border-radius: 50%;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.tip-item p {
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.5;
}

.outfit-section {
  margin-bottom: 25px;
}

.outfit-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.outfit-card {
  background: white;
  padding: 12px;
  border-radius: 14px;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.08);
  text-align: center;
  transition: all 0.3s;
}

.outfit-card:hover {
  transform: translateY(-3px);
}

.outfit-icon {
  font-size: 1.5rem;
  margin-bottom: 6px;
}

.outfit-card h4 {
  font-size: 0.85rem;
  color: #4c1d95;
  margin-bottom: 6px;
}

.outfit-card p {
  font-size: 0.8rem;
  color: #64748b;
}

.outfit-card.spring { border-top: 3px solid #10b981; }
.outfit-card.summer { border-top: 3px solid #f59e0b; }
.outfit-card.autumn { border-top: 3px solid #ef4444; }
.outfit-card.winter { border-top: 3px solid #6366f1; }

.secrets-section {
  margin-bottom: 25px;
}

.secrets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.secret-card {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.1));
  padding: 12px;
  border-radius: 14px;
  transition: all 0.3s;
}

.secret-card:hover {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15));
  transform: scale(1.02);
}

.secret-card h4 {
  font-size: 0.9rem;
  color: #4c1d95;
  margin-bottom: 6px;
}

.secret-card p {
  font-size: 0.8rem;
  color: #64748b;
}

.action-section {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 15px;
  background: linear-gradient(180deg, rgba(248, 246, 252, 0.95), white);
  border-top: 1px solid rgba(99, 102, 241, 0.1);
  margin-top: 10px;
}

.action-btn {
  flex: 1;
  padding: 12px 15px;
  border: none;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.action-btn span {
  font-size: 1rem;
}

.action-btn.consult {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.action-btn.consult:hover,
.action-btn.consult.active {
  background: #6366f1;
  color: white;
}

.action-btn.book {
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.action-btn.book:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.action-btn.favorite {
  background: rgba(236, 72, 153, 0.1);
  color: #ec4899;
}

.action-btn.favorite.active {
  background: #ec4899;
  color: white;
}

.action-btn.favorite:hover {
  background: #ec4899;
  color: white;
}

/* ===== 客服聊天面板 ===== */
.chat-panel {
  margin-top: 10px;
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(99, 102, 241, 0.15);
  overflow: hidden;
}

.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}

.chat-slide-enter-to,
.chat-slide-leave-from {
  opacity: 1;
  max-height: 400px;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(236, 72, 153, 0.08));
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.chat-header-icon {
  font-size: 1.4rem;
}

.chat-header h4 {
  font-size: 0.9rem;
  color: #4c1d95;
  margin: 0;
}

.chat-status {
  font-size: 0.75rem;
  color: #10b981;
}

.chat-messages {
  max-height: 200px;
  overflow-y: auto;
  padding: 12px 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.2) transparent;
}

.chat-messages::-webkit-scrollbar {
  width: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.2);
  border-radius: 2px;
}

.chat-message {
  display: flex;
}

.user-msg {
  justify-content: flex-end;
}

.bot-msg {
  justify-content: flex-start;
}

.msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 0.85rem;
  line-height: 1.5;
  word-break: break-word;
}

.user-msg .msg-bubble {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: white;
  border-bottom-right-radius: 4px;
}

.bot-msg .msg-bubble {
  background: #f1f5f9;
  color: #475569;
  border-bottom-left-radius: 4px;
}

.msg-bubble.typing {
  color: #94a3b8;
  font-style: italic;
}

.typing-dots {
  animation: blink 1.2s infinite;
}

@keyframes blink {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  80%, 100% { opacity: 0; }
}

.chat-quick-questions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 0 15px 10px;
}

.quick-q-btn {
  padding: 6px 12px;
  background: rgba(99, 102, 241, 0.08);
  color: #6366f1;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 16px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-q-btn:hover {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 10px 15px;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 20px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #6366f1;
}

.chat-send-btn {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-send-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.chat-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== 预约报名弹窗 ===== */
.booking-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 20, 50, 0.5);
  backdrop-filter: blur(4px);
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.booking-fade-enter-active,
.booking-fade-leave-active {
  transition: all 0.3s ease;
}

.booking-fade-enter-from,
.booking-fade-leave-to {
  opacity: 0;
}

.booking-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
  position: relative;
}

.booking-close {
  position: absolute;
  top: 12px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.booking-close:hover {
  color: #6366f1;
}

.booking-title {
  font-size: 1.3rem;
  color: #4c1d95;
  margin-bottom: 5px;
}

.booking-dest {
  font-size: 0.9rem;
  color: #6366f1;
  margin-bottom: 20px;
}

.booking-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 14px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
  background: #fafafe;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #6366f1;
  background: white;
}

.form-group textarea {
  resize: vertical;
  min-height: 50px;
}

.form-error {
  font-size: 0.78rem;
  color: #ef4444;
}

.number-picker {
  display: flex;
  align-items: center;
  gap: 15px;
}

.number-picker button {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: white;
  color: #6366f1;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.number-picker button:hover:not(:disabled) {
  background: #6366f1;
  color: white;
}

.number-picker button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.number-value {
  font-size: 1rem;
  font-weight: 600;
  color: #4c1d95;
  min-width: 36px;
  text-align: center;
}

.booking-submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 5px;
}

.booking-submit-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

/* 预约成功 */
.booking-success {
  text-align: center;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.booking-success h3 {
  font-size: 1.3rem;
  color: #4c1d95;
  margin-bottom: 15px;
}

.success-info {
  text-align: left;
  background: rgba(99, 102, 241, 0.05);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
}

.success-info p {
  font-size: 0.85rem;
  color: #475569;
  padding: 5px 0;
  margin: 0;
}

.success-tip {
  font-size: 0.85rem;
  color: #10b981;
  margin-bottom: 20px;
}

/* ===== 响应式适配 ===== */
@media (min-width: 768px) {
  .modal-container {
    max-width: 600px;
    max-height: 85vh;
    border-radius: 28px;
  }

  .carousel-section {
    height: 280px;
  }

  .modal-content {
    padding: 25px;
    max-height: calc(85vh - 280px);
  }

  .destination-title {
    font-size: 2.2rem;
  }

  .attractions-grid,
  .outfit-grid,
  .secrets-grid,
  .price-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .action-section {
    justify-content: center;
    gap: 15px;
  }

  .action-btn {
    padding: 14px 25px;
    font-size: 0.9rem;
  }

  .chat-messages {
    max-height: 240px;
  }
}
</style>
