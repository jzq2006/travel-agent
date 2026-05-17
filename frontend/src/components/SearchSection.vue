<template>
  <section class="search-section">
    <div class="search-title">
      <h2>规划您的完美旅程</h2>
      <p>告诉我们您的偏好，获取专属旅行建议</p>
    </div>
    <form class="search-form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>📍 目的地</label>
        <input type="text" v-model="destination" placeholder="您想去哪里？">
      </div>
      <div class="form-group">
        <label>🎯 旅行类型</label>
        <select v-model="travelType">
          <option value="">选择类型</option>
          <option value="adventure">🏔️ 探险之旅</option>
          <option value="relaxation">💆 休闲度假</option>
          <option value="culture">🏛️ 文化体验</option>
          <option value="nature">🌿 自然风光</option>
          <option value="food">🍜 美食之旅</option>
          <option value="romantic">💕 浪漫之旅</option>
          <option value="family">👨‍👩‍👧‍👦 亲子游</option>
        </select>
      </div>
      <div class="form-group">
        <label>💰 预算（元/人）</label>
        <input type="number" v-model="budget" placeholder="输入预算金额" min="100">
      </div>
      <div class="form-group">
        <label>📅 旅行天数</label>
        <input type="number" v-model="duration" placeholder="几天？" min="1" max="90">
      </div>
      <div class="form-group date-range-with-people">
        <div class="date-range-section">
          <div class="field-header">
            <label>🗓️ 意向时段</label>
            <small class="date-hint">在选定日期范围内，智能匹配最优时间</small>
          </div>
          <div class="date-inputs">
            <input type="date" v-model="startDate" placeholder="开始日期">
            <span class="date-separator">至</span>
            <input type="date" v-model="endDate" placeholder="结束日期">
          </div>
        </div>
        <div class="people-count-section">
          <label>👥 出行人数</label>
          <input type="number" v-model="peopleCount" placeholder="几人出行？" min="1" max="50">
        </div>
        <div class="travel-preferences-section">
          <label>✨ 出行偏好</label>
          <div class="preference-tags">
            <button
              v-for="pref in preferences"
              :key="pref.type"
              :class="['pref-tag', { active: selectedPreferences.includes(pref.type) }]"
              @click="togglePreference(pref.type)"
              type="button"
            >
              {{ pref.icon }} {{ pref.label }}
            </button>
          </div>
        </div>
      </div>
      <div class="form-group full-width">
        <label>🍽️ 饮食要求</label>
        <textarea v-model="dietaryRequirements" placeholder="例如：素食、清真、海鲜过敏、喜欢川菜等..."></textarea>
      </div>
      <div class="form-group full-width">
        <label>🎯 想去的景点</label>
        <textarea v-model="desiredAttractions" placeholder="例如：故宫、长城、西湖、兵马俑等..."></textarea>
      </div>
      <div class="form-group full-width">
        <label>📝 备注</label>
        <textarea v-model="remarks" placeholder="其他需要说明的需求或注意事项（选填）..." rows="2"></textarea>
      </div>
      <button type="submit" class="btn-search" :disabled="isLoading">
        {{ isLoading ? '🤔 Agent 正在规划...' : '🚀 获取建议' }}
      </button>
    </form>
    <div class="quick-filters">
      <button
        v-for="filter in filters"
        :key="filter.type"
        :class="['filter-chip', { active: travelType === filter.type }]"
        @click="setFilter(filter.type)"
      >
        {{ filter.label }}
      </button>
    </div>

    <!-- Agent 实时思考过程 -->
    <div v-if="isLoading" class="agent-process">
      <div class="agent-process-header">
        <div class="loading-spinner"></div>
        <span>AI Agent 实时思考过程</span>
      </div>
      <div class="agent-steps">
        <div v-for="(step, i) in agentSteps" :key="i" class="agent-step">
          <template v-if="step.type === 'agent_start'">
            <div class="step-badge start">▶</div>
            <span class="step-text start-text">{{ step.message }}</span>
          </template>
          <template v-else-if="step.type === 'tool_call'">
            <div class="step-badge tool">🔧</div>
            <span class="step-text">
              调用工具：<strong>{{ toolNameMap[step.tool] || step.tool }}</strong>
              <span class="step-args" v-if="step.args && Object.keys(step.args).length">
                （{{ formatArgs(step.args) }}）
              </span>
            </span>
          </template>
          <template v-else-if="step.type === 'tool_result'">
            <div class="step-badge result">📊</div>
            <span class="step-text result-text">{{ step.result.slice(0, 120) }}{{ step.result.length > 120 ? '...' : '' }}</span>
          </template>
          <template v-else-if="step.type === 'done'">
            <div class="step-badge done">✅</div>
            <span class="step-text done-text">规划完成，耗时 {{ step.duration_ms }}ms</span>
          </template>
        </div>
        <div v-if="isLoading && !planResult" class="agent-step">
          <div class="loading-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI生成方案结果 -->
    <transition name="plan-fade">
      <div v-if="planResult" class="plan-result">
        <div class="plan-header">
          <h3>AI为您定制的专属旅行方案</h3>
          <button @click="planResult = ''" class="close-plan">&times;</button>
        </div>
        <div class="plan-content">{{ planResult }}</div>

        <!-- 追问入口按钮 -->
        <button class="plan-chat-trigger" @click="showPlanChat = true">
          💬 对方案有疑问？点击追问
        </button>

        <!-- 追问聊天窗口 -->
        <transition name="chat-slide">
          <div v-if="showPlanChat" class="plan-chat-panel">
            <div class="plan-chat-header">
              <span>💬 行程追问</span>
              <button class="plan-chat-close" @click="showPlanChat = false">&times;</button>
            </div>
            <div class="plan-chat-messages" ref="chatMessagesRef">
              <div v-if="planChatMessages.length === 0" class="plan-chat-empty">
                对生成的方案有任何疑问或想调整的地方，随时告诉我
              </div>
              <div
                v-for="(msg, i) in planChatMessages"
                :key="i"
                :class="['plan-chat-bubble', msg.role === 'user' ? 'bubble-user' : 'bubble-ai']"
              >
                {{ msg.text }}
              </div>
              <div v-if="planChatLoading" class="plan-chat-bubble bubble-ai">
                <span class="typing-dots"><span></span><span></span><span></span></span>
              </div>
            </div>
            <div class="plan-chat-input-bar">
              <input
                v-model="planChatInput"
                @keyup.enter="sendPlanChat"
                placeholder="例如：第三天能换成爬长城吗？"
                :disabled="planChatLoading"
              />
              <button @click="sendPlanChat" :disabled="planChatLoading || !planChatInput.trim()">
                发送
              </button>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </section>
</template>

<script>
import api from '../api'

export default {
  name: 'SearchSection',
  inject: ['getUser', 'requestLogin'],
  data() {
    return {
      destination: '',
      travelType: '',
      budget: '',
      duration: '',
      peopleCount: '',
      startDate: '',
      endDate: '',
      dietaryRequirements: '',
      desiredAttractions: '',
      remarks: '',
      selectedPreferences: [],
      isLoading: false,
      planResult: '',
      agentSteps: [],
      // 追问聊天状态
      showPlanChat: false,      // 追问窗口是否显示
      planChatInput: '',         // 追问输入框内容
      planChatMessages: [],      // 追问对话历史 [{role:'user'|'assistant', text:'...'}]
      planChatLoading: false,    // 追问是否正在等待回复
      toolNameMap: {
        query_weather: '查询天气',
        search_attractions: '搜索景点',
        plan_route: '规划路线',
        search_hotels_nearby: '搜索酒店',
        geocode_address: '地理编码',
      },
      preferences: [
        { type: 'photography', label: '拍照', icon: '📸' },
        { type: 'shopping', label: '购物', icon: '🛍️' },
        { type: 'hiking', label: '徒步', icon: '🥾' },
        { type: 'nightlife', label: '夜生活', icon: '🌃' },
        { type: 'history', label: '历史', icon: '🏛️' },
        { type: 'local', label: '本地体验', icon: '🎭' }
      ],
      filters: [
        { type: 'adventure', label: '🏔️ 探险' },
        { type: 'relaxation', label: '💆 度假' },
        { type: 'culture', label: '🏛️ 文化' },
        { type: 'nature', label: '🌿 自然' },
        { type: 'food', label: '🍜 美食' },
        { type: 'romantic', label: '💕 浪漫' },
        { type: 'family', label: '👨‍👩‍👧‍👦 亲子' }
      ]
    }
  },
  methods: {
    async handleSubmit() {
      if (!this.getUser()) {
        alert('请先登录后再使用此功能')
        this.requestLogin()
        return
      }
      if (!this.destination.trim()) {
        alert('请输入目的地')
        return
      }
      if (!this.duration || this.duration < 1) {
        alert('请输入旅行天数')
        return
      }
      if (!this.budget || Number(this.budget) < 100) {
        alert('请输入预算金额（至少100元）')
        return
      }

      const requestBody = {
        destination: this.destination,
        travelType: this.travelType || 'culture',
        budget: Number(this.budget),
        duration: Number(this.duration),
        peopleCount: Number(this.peopleCount) || 2,
        startDate: this.startDate,
        endDate: this.endDate,
        dietaryRequirements: this.dietaryRequirements,
        desiredAttractions: this.desiredAttractions,
        remarks: this.remarks,
        selectedPreferences: this.selectedPreferences,
      }

      this.isLoading = true
      this.planResult = ''
      this.agentSteps = []

      try {
        // Use SSE streaming endpoint
        const token = localStorage.getItem('token')
        const response = await fetch('/api/generate-plan/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify(requestBody),
        })

        if (!response.ok) {
          const errData = await response.json().catch(() => null)
          const msg = errData?.detail || `请求失败 (${response.status})`
          throw new Error(msg)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const raw = line.slice(6).trim()
            if (!raw) continue
            try {
              const event = JSON.parse(raw)
              this.agentSteps.push(event)

              if (event.type === 'final_answer') {
                this.planResult = event.content
              }
            } catch { /* ignore parse errors */ }
          }
        }

        if (!this.planResult) {
          throw new Error('未收到方案结果')
        }

        this.$nextTick(() => {
          const el = document.querySelector('.plan-result')
          if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
        })
      } catch (err) {
        // Show error or fallback to non-streaming endpoint
        const errMsg = err.message || ''
        if (errMsg && errMsg !== '未收到方案结果') {
          alert(errMsg)
        } else {
          try {
            const { data } = await api.post('/generate-plan', requestBody)
            this.planResult = data.plan
          } catch (err2) {
            const msg = err2.response?.data?.detail || '生成方案失败，请稍后重试'
            alert(msg)
          }
        }
      } finally {
        this.isLoading = false
        // 方案生成完，重置追问状态，打开追问入口
        this.showPlanChat = false
        this.planChatMessages = []
        this.planChatInput = ''
      }
    },
    async sendPlanChat() {
      const msg = this.planChatInput.trim()
      if (!msg || this.planChatLoading) return

      this.planChatMessages.push({ role: 'user', text: msg })
      this.planChatInput = ''
      this.planChatLoading = true

      try {
        const token = localStorage.getItem('token')
        const response = await fetch('/api/chat/plan', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            destination: this.destination,
            plan_text: this.planResult,
            message: msg,
            history: this.planChatMessages.slice(0, -1),
          }),
        })

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let reply = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const raw = line.slice(6).trim()
            if (!raw) continue
            try {
              const event = JSON.parse(raw)
              if (event.type === 'final_answer') {
                reply = event.content
              }
            } catch { /* ignore parse errors */ }
          }
        }

        this.planChatMessages.push({ role: 'assistant', text: reply || '（未获取到回复）' })
      } catch (err) {
        this.planChatMessages.push({
          role: 'assistant',
          text: '抱歉，追问服务暂时不可用，请稍后重试。',
        })
      } finally {
        this.planChatLoading = false
        this.$nextTick(() => {
          const el = this.$refs.chatMessagesRef
          if (el) el.scrollTop = el.scrollHeight
        })
      }
    },
    formatArgs(args) {
      return Object.entries(args)
        .filter(([, v]) => v)
        .map(([k, v]) => `${k}=${typeof v === 'string' ? v : JSON.stringify(v)}`)
        .join(', ')
    },
    setFilter(type) {
      this.travelType = type
    },
    togglePreference(type) {
      const index = this.selectedPreferences.indexOf(type)
      if (index > -1) {
        this.selectedPreferences.splice(index, 1)
      } else {
        this.selectedPreferences.push(type)
      }
    }
  }
}
</script>

<style scoped>
.search-section {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-radius: 30px;
  padding: 50px;
  margin: -60px auto 50px;
  max-width: 1100px;
  position: relative;
  z-index: 10;
  box-shadow: 0 30px 100px rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.5);
}

.search-title {
  text-align: center;
  margin-bottom: 35px;
}

.search-title h2 {
  font-size: 2rem;
  color: var(--dark);
  margin-bottom: 10px;
}

.search-title p {
  color: #64748b;
  font-size: 1.05rem;
}

.search-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
  align-items: end;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 12px;
  font-weight: 600;
  color: var(--dark);
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group input,
.form-group select {
  padding: 18px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 1.05rem;
  transition: all 0.3s;
  background: #f8fafc;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
  background: white;
  box-shadow: 0 0 0 5px rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
}

.form-group textarea {
  padding: 18px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 1.05rem;
  transition: all 0.3s;
  background: #f8fafc;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.btn-search {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: white;
  border: none;
  padding: 18px 40px;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-search:hover:not(:disabled) {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 40px rgba(99, 102, 241, 0.4);
}

.btn-search:disabled {
  opacity: 0.8;
  cursor: wait;
}

.quick-filters {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  flex-wrap: wrap;
  justify-content: center;
}

.filter-chip {
  padding: 12px 24px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border: 2px solid #e2e8f0;
  border-radius: 30px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s;
  color: #475569;
  font-weight: 500;
}

.filter-chip:hover {
  border-color: var(--primary);
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(99, 102, 241, 0.2);
}

.filter-chip.active {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border-color: transparent;
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}

.date-range-with-people {
  grid-column: 1 / -1;
  display: flex;
  gap: 25px;
  align-items: flex-start;
}

.date-range-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.field-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.field-header label {
  font-weight: 600;
  color: var(--dark);
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.people-count-section {
  min-width: 200px;
  display: flex;
  flex-direction: column;
}

.travel-preferences-section {
  min-width: 280px;
  display: flex;
  flex-direction: column;
}

.preference-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pref-tag {
  padding: 8px 14px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
  color: #475569;
  font-weight: 500;
  white-space: nowrap;
}

.pref-tag:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.pref-tag.active {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border-color: transparent;
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-inputs input {
  flex: 1;
  padding: 18px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 1.05rem;
  transition: all 0.3s;
  background: #f8fafc;
}

.date-inputs input:focus {
  outline: none;
  border-color: var(--primary);
  background: white;
  box-shadow: 0 0 0 5px rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
}

.date-separator {
  color: #64748b;
  font-weight: 500;
}

.date-hint {
  color: #94a3b8;
  font-size: 0.85rem;
  font-style: italic;
}

/* Agent 思考过程面板 */
.agent-process {
  margin-top: 30px;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(99, 102, 241, 0.2);
}

.agent-process-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  font-size: 0.9rem;
  font-weight: 600;
}

.agent-steps {
  padding: 16px 24px;
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.agent-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  animation: fadeInStep 0.3s ease;
}

@keyframes fadeInStep {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.step-badge {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.step-badge.start { background: rgba(16, 185, 129, 0.2); }
.step-badge.tool { background: rgba(99, 102, 241, 0.2); }
.step-badge.result { background: rgba(245, 158, 11, 0.2); }
.step-badge.done { background: rgba(16, 185, 129, 0.3); }

.step-text {
  color: #94a3b8;
  font-size: 0.85rem;
  line-height: 1.5;
}

.step-text strong { color: #a5b4fc; }
.step-args { color: #64748b; font-size: 0.8rem; }
.start-text { color: #6ee7b7; }
.result-text { color: #fbbf24; }
.done-text { color: #34d399; }

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: #6366f1;
  border-radius: 50%;
  animation: dotPulse 1.2s ease infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.2); }
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(99,102,241,0.3);
  border-top-color: #a5b4fc;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Plan result */
.plan-result {
  margin-top: 30px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(99,102,241,0.15);
  overflow: hidden;
  border: 1px solid rgba(99,102,241,0.1);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 25px;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: white;
}

.plan-header h3 {
  font-size: 1.1rem;
  margin: 0;
}

.close-plan {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 1.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-plan:hover {
  background: rgba(255,255,255,0.35);
}

.plan-content {
  padding: 25px;
  white-space: pre-wrap;
  line-height: 1.8;
  color: #334155;
  font-size: 0.95rem;
  max-height: 600px;
  overflow-y: auto;
}

.plan-fade-enter-active,
.plan-fade-leave-active {
  transition: all 0.4s ease;
}

.plan-fade-enter-from,
.plan-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@media (max-width: 768px) {
  .search-section {
    margin: -40px 15px 40px;
    padding: 30px;
  }
  .search-form {
    grid-template-columns: 1fr;
  }
  .plan-chat-panel {
    max-height: 400px;
  }
}

/* ── 追问入口按钮 ── */
.plan-chat-trigger {
  display: block;
  width: 100%;
  padding: 14px;
  border: none;
  background: linear-gradient(135deg, #f0f0ff, #eef2ff);
  color: #6366f1;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border-top: 1px solid rgba(99, 102, 241, 0.1);
}

.plan-chat-trigger:hover {
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
}

/* ── 追问聊天窗口 ── */
.plan-chat-panel {
  background: #f8fafc;
  border-top: 2px solid rgba(99, 102, 241, 0.15);
  display: flex;
  flex-direction: column;
  max-height: 500px;
}

.plan-chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  color: #334155;
  font-size: 0.95rem;
}

.plan-chat-close {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: #94a3b8;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.plan-chat-close:hover {
  background: #f1f5f9;
  color: #64748b;
}

.plan-chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 120px;
  max-height: 320px;
}

.plan-chat-empty {
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
  padding: 20px 0;
}

.plan-chat-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 0.9rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-user {
  align-self: flex-end;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border-bottom-right-radius: 4px;
}

.bubble-ai {
  align-self: flex-start;
  background: white;
  color: #334155;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.plan-chat-input-bar {
  display: flex;
  gap: 10px;
  padding: 12px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.plan-chat-input-bar input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.plan-chat-input-bar input:focus {
  outline: none;
  border-color: #6366f1;
}

.plan-chat-input-bar button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.plan-chat-input-bar button:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.plan-chat-input-bar button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 打字动画 */
.typing-dots {
  display: inline-flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: dotPulse 1.2s ease infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

/* 窗口滑入动画 */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
}
</style>