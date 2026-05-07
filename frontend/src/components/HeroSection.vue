<template>
  <section class="hero">
    <div class="hero-content">
      <div class="hero-logo">🌏</div>
      <h1>
        <span v-for="(char, index) in titleChars" :key="index">{{ char }}</span>
      </h1>
      <p>智能旅行助手，为您量身定制完美旅程</p>
      <div class="hero-cta" @click="scrollToSearch">
        开始规划旅程 →
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection',
  data() {
    return {
      titleChars: ['探', '索', '中', '国', '，', '发', '现', '精', '彩']
    }
  },
  methods: {
    scrollToSearch() {
      document.querySelector('.search-section').scrollIntoView({ behavior: 'smooth' })
    }
  }
}
</script>

<style scoped>
.hero {
  min-height: 60vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
}

.hero-logo {
  font-size: 5rem;
  margin-bottom: 20px;
  display: inline-block;
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0) rotate(-5deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
}

.hero h1 {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 15px;
  text-shadow: 2px 2px 20px rgba(0,0,0,0.3);
}

.hero h1 span {
  position: relative;
  display: inline-block;
  animation: textWave 2s ease-in-out infinite;
}

.hero h1 span:nth-child(1) { animation-delay: 0s; }
.hero h1 span:nth-child(2) { animation-delay: 0.1s; }
.hero h1 span:nth-child(3) { animation-delay: 0.2s; }
.hero h1 span:nth-child(4) { animation-delay: 0.3s; }
.hero h1 span:nth-child(5) { animation-delay: 0.4s; }
.hero h1 span:nth-child(6) { animation-delay: 0.5s; }
.hero h1 span:nth-child(7) { animation-delay: 0.6s; }
.hero h1 span:nth-child(8) { animation-delay: 0.7s; }
.hero h1 span:nth-child(9) { animation-delay: 0.8s; }

@keyframes textWave {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.hero p {
  font-size: 1.3rem;
  opacity: 0.95;
  margin-bottom: 25px;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 15px;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  padding: 15px 30px;
  border-radius: 50px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(255,255,255,0.3);
}

.hero-cta:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

@media (max-width: 768px) {
  .hero h1 { font-size: 2.2rem; }
  .hero-logo { font-size: 3.5rem; }
}
</style>