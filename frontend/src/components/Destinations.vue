<template>
  <section class="destinations">
    <div class="section-header" :class="{ visible: isVisible }">
      <h2>🌟 国内热门目的地</h2>
      <p>探索祖国大好河山，发现不一样的风景</p>
    </div>
    <div class="destination-grid">
      <div
        v-for="(dest, index) in destinations"
        :key="index"
        class="destination-card"
        :class="{ visible: isVisible }"
        :style="{ transitionDelay: index * 0.1 + 's' }"
        @click="openModal(dest)"
      >
        <div class="destination-gradient" :style="{ backgroundImage: `url(${dest.image})` }">
          <span class="destination-badge">{{ dest.badge }}</span>
          <span class="destination-rating">⭐ {{ dest.rating }}</span>
          <span v-if="isFavorited(dest.name)" class="destination-fav-badge">💖 已收藏</span>
        </div>
        <div class="destination-content">
          <h3>{{ dest.name }}</h3>
          <div class="destination-location">📍 {{ dest.region }}</div>
          <p>{{ dest.description }}</p>
          <div class="destination-tags">
            <span v-for="tag in dest.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <div class="destination-footer">
            <span class="destination-price">{{ dest.price }} <span>/人</span></span>
            <span class="btn-explore">了解更多 →</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 目的地详情弹窗 -->
    <DestinationModal
      :visible="showModal"
      :destination="selectedDestination"
      :is-favorited="isFavorited(selectedDestination.name)"
      @close="closeModal"
      @favorite="addToFavorite"
      @unfavorite="removeFavorite"
    />
  </section>
</template>

<script>
import { destinations } from '../data/destinations'
import DestinationModal from './DestinationModal.vue'

export default {
  name: 'Destinations',
  components: {
    DestinationModal
  },
  data() {
    return {
      destinations,
      isVisible: false,
      showModal: false,
      selectedDestination: {},
      favorites: []
    }
  },
  mounted() {
    this.loadFavorites()
    this.checkVisibility()
    window.addEventListener('scroll', this.checkVisibility)
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.checkVisibility)
  },
  methods: {
    loadFavorites() {
      try {
        const saved = localStorage.getItem('travel-favorites')
        this.favorites = saved ? JSON.parse(saved) : []
      } catch {
        this.favorites = []
      }
    },
    saveFavorites() {
      localStorage.setItem('travel-favorites', JSON.stringify(this.favorites))
    },
    isFavorited(name) {
      return this.favorites.includes(name)
    },
    checkVisibility() {
      const el = document.querySelector('.destinations')
      if (el) {
        const rect = el.getBoundingClientRect()
        this.isVisible = rect.top < window.innerHeight - 50
      }
    },
    openModal(dest) {
      this.selectedDestination = dest
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
    },
    addToFavorite(dest) {
      if (!this.favorites.includes(dest.name)) {
        this.favorites.push(dest.name)
        this.saveFavorites()
      }
    },
    removeFavorite(dest) {
      const idx = this.favorites.indexOf(dest.name)
      if (idx > -1) {
        this.favorites.splice(idx, 1)
        this.saveFavorites()
      }
    }
  }
}
</script>

<style scoped>
.destinations {
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

.destination-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
}

.destination-card {
  background: white;
  border-radius: 25px;
  overflow: hidden;
  box-shadow: 0 15px 50px rgba(0,0,0,0.1);
  transition: all 0.5s;
  cursor: pointer;
  opacity: 0;
  transform: translateY(30px);
}

.destination-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.destination-card:hover {
  transform: translateY(-15px) scale(1.02);
  box-shadow: 0 25px 70px rgba(0,0,0,0.2);
}

.destination-gradient {
  height: 180px;
  position: relative;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.destination-gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.5) 0%, transparent 80%);
  z-index: 1;
}

.destination-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  background: rgba(255,255,255,0.95);
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--primary);
  z-index: 2;
}

.destination-rating {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(255,255,255,0.95);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent);
  z-index: 2;
}

.destination-fav-badge {
  position: absolute;
  bottom: 15px;
  right: 15px;
  background: rgba(236, 72, 153, 0.9);
  padding: 5px 12px;
  border-radius: 16px;
  font-size: 0.78rem;
  font-weight: 600;
  color: white;
  z-index: 2;
}

.destination-content {
  padding: 25px;
}

.destination-content h3 {
  font-size: 1.4rem;
  margin-bottom: 8px;
  color: var(--dark);
}

.destination-location {
  color: #64748b;
  font-size: 0.95rem;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.destination-content p {
  color: #475569;
  font-size: 0.95rem;
  line-height: 1.7;
  margin-bottom: 15px;
}

.destination-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.tag {
  background: linear-gradient(135deg, #f0f4ff, #fef0f5);
  color: var(--primary);
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s;
}

.tag:hover {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
}

.destination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 2px solid #f1f5f9;
}

.destination-price {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary);
}

.destination-price span {
  font-size: 0.85rem;
  font-weight: 400;
  color: #94a3b8;
}

.btn-explore {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s;
  cursor: pointer;
}

.btn-explore:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(99, 102, 241, 0.3);
}

@media (max-width: 768px) {
  .destination-grid {
    grid-template-columns: 1fr;
  }
  .section-header h2 {
    font-size: 2rem;
  }
}
</style>
