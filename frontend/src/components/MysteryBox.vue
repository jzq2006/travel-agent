<template>
  <section class="mystery-box-section">
    <div class="mystery-box-container" :class="{ visible: isVisible }">
      <div class="mystery-box-header">
        <h2>🎁 周末盲盒</h2>
        <p>不知道去哪里？让命运为您决定一个惊喜目的地！</p>
      </div>
      <button
        class="mystery-box-btn"
        :class="{ opening: isOpening }"
        @click="openMysteryBox"
      >
        🎲 开启盲盒
      </button>
      <div class="mystery-result" :class="{ active: showResult }">
        <div class="result-city">
          <div class="result-city-icon">{{ resultCity.icon }}</div>
          <div class="result-city-name">{{ resultCity.name }}</div>
          <div class="result-city-region">{{ resultCity.region }}</div>
        </div>
        <div class="result-style">
          <span
            v-for="(style, index) in resultStyles"
            :key="index"
            class="style-tag"
          >
            {{ style.icon }} {{ style.name }}
          </span>
        </div>
        <div class="result-description">{{ resultCity.description }}</div>
        <div class="result-price">
          <div class="price-item">💰 {{ resultCity.price }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { destinations, travelStyles } from '../data/destinations'

export default {
  name: 'MysteryBox',
  data() {
    return {
      destinations,
      travelStyles,
      isOpening: false,
      showResult: false,
      isVisible: false,
      resultCity: {},
      resultStyles: []
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
      const el = document.querySelector('.mystery-box-container')
      if (el) {
        const rect = el.getBoundingClientRect()
        this.isVisible = rect.top < window.innerHeight - 50
      }
    },
    openMysteryBox() {
      this.isOpening = true
      this.showResult = false

      setTimeout(() => {
        // Random city
        this.resultCity = this.destinations[Math.floor(Math.random() * this.destinations.length)]

        // Random styles (3 unique)
        const shuffledStyles = [...this.travelStyles].sort(() => Math.random() - 0.5)
        this.resultStyles = shuffledStyles.slice(0, 3)

        this.showResult = true
        this.isOpening = false
      }, 600)
    }
  }
}
</script>

<style scoped>
.mystery-box-section {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.mystery-box-container {
  background: linear-gradient(135deg, #1e293b, #334155);
  border-radius: 30px;
  padding: 60px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.mystery-box-container.visible {
  opacity: 1;
  transform: translateY(0);
}

.mystery-box-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 40%);
  animation: rotateGlow 8s linear infinite;
}

@keyframes rotateGlow {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.mystery-box-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.mystery-box-header h2 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.mystery-box-header p {
  color: rgba(255,255,255,0.8);
  font-size: 1.2rem;
}

.mystery-box-btn {
  display: block;
  margin: 0 auto 50px;
  background: linear-gradient(135deg, var(--accent), #fbbf24);
  color: var(--dark);
  border: none;
  padding: 25px 60px;
  border-radius: 20px;
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s;
  position: relative;
  z-index: 1;
  animation: pulseBtn 2s ease-in-out infinite;
}

@keyframes pulseBtn {
  0%, 100% { transform: scale(1); box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3); }
  50% { transform: scale(1.05); box-shadow: 0 15px 40px rgba(245, 158, 11, 0.5); }
}

.mystery-box-btn:hover {
  animation: none;
  transform: scale(1.1);
  box-shadow: 0 20px 50px rgba(245, 158, 11, 0.5);
}

.mystery-box-btn.opening {
  animation: boxOpen 0.6s ease-out;
}

@keyframes boxOpen {
  0% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(0.9) rotate(-5deg); }
  50% { transform: scale(1.2) rotate(5deg); }
  75% { transform: scale(0.95) rotate(-3deg); }
  100% { transform: scale(1) rotate(0deg); }
}

.mystery-result {
  display: none;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  padding: 40px;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255,255,255,0.2);
  animation: resultAppear 0.5s ease-out;
}

.mystery-result.active {
  display: block;
}

@keyframes resultAppear {
  0% { opacity: 0; transform: translateY(30px) scale(0.9); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

.result-city {
  text-align: center;
  margin-bottom: 30px;
}

.result-city-icon {
  font-size: 4rem;
  margin-bottom: 15px;
  animation: iconBounce 1s ease-out;
}

@keyframes iconBounce {
  0% { transform: scale(0); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.result-city-name {
  color: white;
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.result-city-region {
  color: rgba(255,255,255,0.7);
  font-size: 1.2rem;
}

.result-style {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.style-tag {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 12px 25px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  animation: tagPop 0.3s ease-out backwards;
}

.style-tag:nth-child(1) { animation-delay: 0.1s; }
.style-tag:nth-child(2) { animation-delay: 0.2s; }
.style-tag:nth-child(3) { animation-delay: 0.3s; }

@keyframes tagPop {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.result-description {
  color: rgba(255,255,255,0.9);
  font-size: 1.1rem;
  line-height: 1.8;
  text-align: center;
  padding: 25px;
  background: rgba(255,255,255,0.05);
  border-radius: 15px;
  margin-bottom: 25px;
}

.result-price {
  display: flex;
  justify-content: center;
  color: white;
}

.price-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .mystery-box-container {
    padding: 40px 25px;
  }
  .mystery-box-btn {
    padding: 20px 40px;
    font-size: 1.1rem;
  }
  .result-city-name {
    font-size: 2rem;
  }
}
</style>