<template>
  <section class="tips-section">
    <div class="section-header" :class="{ visible: isVisible }">
      <h2>💡 旅行小贴士</h2>
      <p>实用建议，让旅途更加顺畅</p>
    </div>
    <div class="tips-grid">
      <div
        v-for="(tip, index) in tips"
        :key="index"
        class="tip-card"
        :class="{ visible: isVisible }"
        :style="{ transitionDelay: index * 0.1 + 's' }"
      >
        <div class="tip-icon">{{ tip.icon }}</div>
        <h4>{{ tip.title }}</h4>
        <p>{{ tip.description }}</p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TipsSection',
  data() {
    return {
      isVisible: false,
      tips: [
        { icon: '📋', title: '提前规划', description: '制定详细的行程计划，预订机票酒店，了解目的地天气和文化习俗。' },
        { icon: '🎒', title: '精简行李', description: '只带必需品，选择多功能物品，预留购物空间，轻装上阵更轻松。' },
        { icon: '💳', title: '财务安全', description: '分散存放现金和卡片，准备应急资金，了解当地消费水平。' },
        { icon: '📱', title: '保持联络', description: '离线地图必备，下载当地交通APP，与家人保持联系。' },
        { icon: '🍽️', title: '品尝美食', description: '勇于尝试当地特色美食，查看大众点评高分店铺。' },
        { icon: '📸', title: '记录美好', description: '记录旅途中的美好瞬间，但也要放下设备用心感受当下。' }
      ]
    }
  },
  mounted() {
    this.checkVisibility()
    window.addEventListener('scroll', this.checkVisibility)
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.checkVisibility)
  },
  methods: {
    checkVisibility() {
      const el = document.querySelector('.tips-section')
      if (el) {
        const rect = el.getBoundingClientRect()
        this.isVisible = rect.top < window.innerHeight - 50
      }
    }
  }
}
</script>

<style scoped>
.tips-section {
  padding: 80px 20px;
  max-width: 1300px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 50px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.section-header.visible {
  opacity: 1;
  transform: translateY(0);
}

.section-header h2 {
  font-size: 2.5rem;
  color: var(--dark);
  margin-bottom: 15px;
}

.section-header p {
  color: #64748b;
  font-size: 1.2rem;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 25px;
}

.tip-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.08);
  transition: all 0.3s;
  opacity: 0;
  transform: translateY(30px);
}

.tip-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.tip-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.12);
}

.tip-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f0f4ff, #fef0f5);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  margin-bottom: 20px;
}

.tip-card h4 {
  color: var(--dark);
  margin-bottom: 12px;
  font-size: 1.15rem;
}

.tip-card p {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.7;
}

@media (max-width: 768px) {
  .tips-grid {
    grid-template-columns: 1fr;
  }
}
</style>