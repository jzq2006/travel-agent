<template>
  <footer>
    <div class="footer-content">
      <div class="footer-brand">
        <h3>🌏 旅行助手</h3>
        <p>让每一次旅行都成为难忘的回忆。我们致力于为您提供最专业、最贴心的旅行规划服务。</p>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© 旅行助手 | 让旅行更简单 | 用心服务每一位旅行者</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>

<style scoped>
footer {
  background: var(--dark);
  padding: 60px 20px 30px;
  color: white;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-brand h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.footer-brand p {
  color: rgba(255,255,255,0.6);
  line-height: 1.7;
}

.footer-bottom {
  text-align: center;
  padding-top: 30px;
  border-top: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.5);
}
</style>