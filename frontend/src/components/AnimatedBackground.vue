<template>
  <div class="background-container">
    <!-- Animated Background -->
    <div class="animated-bg"></div>
    <!-- Particles -->
    <div class="particles">
      <div
        v-for="(particle, index) in particles"
        :key="index"
        class="particle"
        :style="particle.style"
      ></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnimatedBackground',
  data() {
    return {
      particles: []
    }
  },
  mounted() {
    this.createParticles()
  },
  methods: {
    createParticles() {
      for (let i = 0; i < 25; i++) {
        this.particles.push({
          style: {
            left: Math.random() * 100 + '%',
            animationDuration: (12 + Math.random() * 18) + 's',
            animationDelay: Math.random() * 15 + 's',
            width: (3 + Math.random() * 3) + 'px',
            height: (3 + Math.random() * 3) + 'px',
            opacity: 0.3 + Math.random() * 0.5
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.animated-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: bgShift 15s ease-in-out infinite alternate;
}

@keyframes bgShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: floatParticle 15s infinite linear;
}

@keyframes floatParticle {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% {
    transform: translateY(-100vh) rotate(720deg);
    opacity: 0;
  }
}
</style>