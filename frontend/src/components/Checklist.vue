<template>
  <section class="checklist-section">
    <div class="checklist-container" :class="{ visible: isVisible }">
      <div class="checklist-header">
        <h3>📋 旅行准备清单</h3>
        <div class="checklist-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercentage }"></div>
          </div>
          <span class="progress-text">{{ checkedCount }}/{{ totalItems }} 完成</span>
        </div>
      </div>
      <div class="checklist-categories">
        <div v-for="category in categories" :key="category.name" class="checklist-category">
          <h4>{{ category.icon }} {{ category.name }}</h4>
          <label
            v-for="(item, index) in category.items"
            :key="index"
            class="checklist-item"
          >
            <input
              type="checkbox"
              v-model="item.checked"
              @change="updateProgress"
            >
            <span class="checkbox"></span>
            <span>{{ item.text }}</span>
          </label>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Checklist',
  data() {
    return {
      isVisible: false,
      categories: [
        {
          name: '证件类',
          icon: '📄',
          items: [
            { text: '身份证', checked: false },
            { text: '学生证/老年证', checked: false },
            { text: '机票/车票确认', checked: false }
          ]
        },
        {
          name: '行李类',
          icon: '🧳',
          items: [
            { text: '衣物', checked: false },
            { text: '洗漱用品', checked: false },
            { text: '充电器/充电宝', checked: false }
          ]
        },
        {
          name: '健康类',
          icon: '💊',
          items: [
            { text: '常备药品', checked: false },
            { text: '防晒/防蚊用品', checked: false },
            { text: '口罩（备用）', checked: false }
          ]
        },
        {
          name: '电子类',
          icon: '📱',
          items: [
            { text: '离线地图', checked: false },
            { text: '当地交通APP', checked: false },
            { text: '紧急联系方式', checked: false }
          ]
        }
      ]
    }
  },
  computed: {
    totalItems() {
      return this.categories.reduce((sum, cat) => sum + cat.items.length, 0)
    },
    checkedCount() {
      return this.categories.reduce((sum, cat) =>
        sum + cat.items.filter(item => item.checked).length, 0
      )
    },
    progressPercentage() {
      return (this.checkedCount / this.totalItems) * 100 + '%'
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
      const el = document.querySelector('.checklist-container')
      if (el) {
        const rect = el.getBoundingClientRect()
        this.isVisible = rect.top < window.innerHeight - 50
      }
    },
    updateProgress() {
      // Progress is computed automatically
    }
  }
}
</script>

<style scoped>
.checklist-section {
  padding: 80px 20px;
  background: linear-gradient(180deg, #f8fafc, #f1f5f9);
}

.checklist-container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 25px;
  padding: 50px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.checklist-container.visible {
  opacity: 1;
  transform: translateY(0);
}

.checklist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
  gap: 20px;
}

.checklist-header h3 {
  font-size: 1.7rem;
  color: var(--dark);
}

.checklist-progress {
  display: flex;
  align-items: center;
  gap: 20px;
}

.progress-bar {
  width: 200px;
  height: 10px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--success), #34d399);
  border-radius: 10px;
  transition: width 0.5s;
}

.progress-text {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 600;
}

.checklist-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 30px;
}

.checklist-category h4 {
  font-size: 1.05rem;
  color: var(--dark);
  margin-bottom: 20px;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  cursor: pointer;
  transition: all 0.3s;
}

.checklist-item:hover {
  transform: translateX(8px);
}

.checklist-item input {
  display: none;
}

.checklist-item .checkbox {
  width: 24px;
  height: 24px;
  border: 3px solid #cbd5e1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.checklist-item input:checked + .checkbox {
  background: linear-gradient(135deg, var(--success), #34d399);
  border-color: transparent;
}

.checklist-item .checkbox::after {
  content: '✓';
  color: white;
  font-size: 0.85rem;
  opacity: 0;
  transform: scale(0);
  transition: all 0.3s;
}

.checklist-item input:checked + .checkbox::after {
  opacity: 1;
  transform: scale(1);
}

.checklist-item span:last-child {
  color: #475569;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.checklist-item input:checked ~ span:last-child {
  text-decoration: line-through;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .checklist-container {
    padding: 30px;
  }
}
</style>