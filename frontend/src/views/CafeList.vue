<template>
  <div class="cafe-search-page">
    <!-- 히어로 검색 영역 -->
    <section class="search-hero">
      <h1 class="hero-title">
        나만의 <span class="accent">카페</span>를 찾아보세요
      </h1>
      <p class="hero-subtitle">분위기, 감성, 맛까지 — 당신에게 딱 맞는 카페</p>
      
      <div class="search-container">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="카페 이름으로 검색..."
            @keydown.enter="handleSearch"
          />
          <button v-if="searchQuery" class="search-clear" @click="clearSearch">✕</button>
          <button class="search-btn" @click="handleSearch">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 빠른 필터 태그 -->
      <div class="quick-filters">
        <button
          v-for="tag in quickTags"
          :key="tag.value"
          :class="['filter-tag', { active: selectedTag === tag.value }]"
          @click="toggleTag(tag.value)"
        >
          <span class="tag-emoji">{{ tag.emoji }}</span>
          {{ tag.label }}
        </button>
      </div>
    </section>

    <!-- 지도 섹션 -->
    <section class="map-section">
      <KakaoMap
        :cafes="top50Cafes"
        :center-lat="mapCenter.lat"
        :center-lng="mapCenter.lng"
        @center-changed="onMapCenterChanged"
        @bounds-changed="onMapBoundsChanged"
      />
    </section>

    <!-- 결과 섹션 -->
    <section class="results-section">
      <div class="results-header">
        <h2 class="results-title">
          <template v-if="searchQuery || selectedTag">
            검색 결과
            <span class="results-count">{{ filteredCafes.length }}개</span>
          </template>
          <template v-else>
            🗺️ 지도에 보이는 카페
            <span class="results-count">{{ filteredCafes.length }}개</span>
          </template>
        </h2>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>카페를 찾고 있어요...</p>
      </div>

      <!-- 결과 없음 -->
      <div v-else-if="filteredCafes.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>검색 결과가 없습니다</p>
        <p class="empty-hint">다른 키워드로 검색해보세요</p>
      </div>

      <!-- 컴팩트 리스트 -->
      <div v-else class="cafe-list">
        <div
          v-for="cafe in displayedCafes"
          :key="cafe.id"
          class="cafe-item"
          @click="goToDetail(cafe.id)"
        >
          <div class="cafe-thumb-wrapper">
            <img :src="cafe.mainImageUrl" :alt="cafe.name" class="cafe-thumb" loading="lazy" />
          </div>
          
          <div class="cafe-info">
            <div class="cafe-info-top">
              <h3 class="cafe-name">{{ cafe.name }}</h3>
              <div class="cafe-top-badges">
                <span v-if="cafe.creamaScore != null" class="creama-score" :class="scoreClass(cafe.creamaScore)">
                  ★ {{ cafe.creamaScore.toFixed(1) }}
                </span>
                <span v-if="cafe.distance !== null && cafe.distance !== undefined" class="cafe-distance">
                  {{ formatDistance(cafe.distance) }}
                </span>
              </div>
            </div>
            <p class="cafe-address">{{ cafe.address }}</p>
            
            <div class="cafe-meta">
              <!-- 맛 점수 (평균) -->
              <div class="meta-badges">
                <span class="meta-badge taste" v-if="getAvgTaste(cafe) > 0">
                  ☕ {{ getAvgTaste(cafe).toFixed(1) }}
                </span>
                <span class="meta-badge noise" v-if="getSensory(cafe, 'noiseLevel') !== null">
                  🔇 {{ getSensory(cafe, 'noiseLevel') }}
                </span>
                <span class="meta-badge light" v-if="getSensory(cafe, 'lighting') !== null">
                  💡 {{ getSensory(cafe, 'lighting') }}
                </span>
              </div>
              
              <!-- 감성 태그 -->
              <div class="cafe-tags">
                <span
                  v-for="vibe in getVibeKeywords(cafe).slice(0, 3)"
                  :key="vibe"
                  class="vibe-tag"
                >
                  #{{ vibe }}
                </span>
              </div>
            </div>

            <!-- 추천 용도 -->
            <div class="cafe-purposes" v-if="getRecommendedFor(cafe).length > 0">
              <span
                v-for="purpose in getRecommendedFor(cafe).slice(0, 3)"
                :key="purpose"
                class="purpose-badge"
              >
                {{ purpose }}
              </span>
            </div>
          </div>
          
          <div class="cafe-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- 무한스크롤 sentinel + 더보기 표시 -->
      <div v-if="!loading && filteredCafes.length > 0" class="load-more-area">
        <div ref="sentinel" class="sentinel"></div>
        <div v-if="displayCount < filteredCafes.length" class="loading-more">
          <div class="loading-spinner-sm"></div>
        </div>
        <p v-else-if="filteredCafes.length > PAGE_SIZE" class="all-loaded">
          전체 {{ filteredCafes.length }}개 카페를 모두 불러왔어요 ☕
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import KakaoMap from '../components/KakaoMap.vue'

const PAGE_SIZE = 20

const router = useRouter()

interface SensoryData {
  acidity: number
  body: number
  sweetness: number
  bitterness: number
  aroma: number
  noiseLevel: number
  lighting: number
  comfort: number
  musicGenre: string
  crowdedness: number
  hasConcent: boolean
  hasWifi: boolean
  hasParking: boolean
  seatTypes: string[]
  vibeKeywords: string[]
  recommendedFor: string[]
  keywords: string[]
}

interface Cafe {
  id: number
  name: string
  address: string
  latitude: number
  longitude: number
  mainImageUrl: string
  phone: string
  operatingHours: string
  imageUrls: string[]
  sensoryData: SensoryData[]
  distance?: number
  creamaScore?: number
}

const cafes = ref<Cafe[]>([])
const searchQuery = ref('')
const selectedTag = ref('')
const loading = ref(true)
const locationAvailable = ref(false)
const displayCount = ref(PAGE_SIZE)
const sentinel = ref<HTMLElement | null>(null)
const mapCenter = ref({ lat: 37.5488, lng: 127.0877 })
const mapBounds = ref<{ swLat: number; swLng: number; neLat: number; neLng: number } | null>(null)
let observer: IntersectionObserver | null = null

const quickTags = [
  { emoji: '🤫', label: '조용한', value: '조용' },
  { emoji: '💑', label: '데이트', value: '데이트' },
  { emoji: '💻', label: '작업', value: '작업' },
  { emoji: '📸', label: '사진', value: '사진' },
  { emoji: '🌿', label: '자연', value: '자연' },
  { emoji: '🎵', label: '음악', value: '음악' },
  { emoji: '📚', label: '독서', value: '독서' },
  { emoji: '🌙', label: '야간', value: '야간' },
]

// 태그/검색 필터만 적용된 전체 카페 (지도 마커용)
const allFilteredCafes = computed(() => {
  let result = cafes.value
  if (selectedTag.value) {
    result = result.filter(cafe => {
      const sd = cafe.sensoryData?.[0]
      if (!sd) return false
      const allText = [
        ...(sd.vibeKeywords || []),
        ...(sd.recommendedFor || []),
        ...(sd.keywords || []),
      ].join(' ').toLowerCase()
      return allText.includes(selectedTag.value)
    })
  }
  return result
})

// 지도 bounds 내 카페만 필터링 (목록용)
const filteredCafes = computed(() => {
  let result = allFilteredCafes.value
  if (mapBounds.value) {
    const { swLat, swLng, neLat, neLng } = mapBounds.value
    result = result.filter(cafe => {
      if (!cafe.latitude || !cafe.longitude) return false
      return (
        cafe.latitude >= swLat && cafe.latitude <= neLat &&
        cafe.longitude >= swLng && cafe.longitude <= neLng
      )
    })
  }
  return result
})

// 지도 마커용: 점수 상위 50개만 표시
const top50Cafes = computed(() => {
  return [...allFilteredCafes.value]
    .filter(c => c.creamaScore && c.creamaScore > 0)
    .sort((a, b) => (b.creamaScore ?? 0) - (a.creamaScore ?? 0))
    .slice(0, 50)
})

// 실제 화면에 보여줄 슬라이스
const displayedCafes = computed(() => filteredCafes.value.slice(0, displayCount.value))

// 검색/필터 변경 시 표시 개수 리셋
watch([filteredCafes], () => {
  displayCount.value = PAGE_SIZE
})

function getAvgTaste(cafe: Cafe): number {
  const sd = cafe.sensoryData?.[0]
  if (!sd) return 0
  return (sd.acidity + sd.body + sd.sweetness + sd.bitterness + sd.aroma) / 5
}

function scoreClass(score: number): string {
  if (score >= 7.5) return 'score-high'
  if (score >= 5.0) return 'score-mid'
  return 'score-low'
}

function getSensory(cafe: Cafe, field: keyof SensoryData): any {
  return cafe.sensoryData?.[0]?.[field] ?? null
}

function getVibeKeywords(cafe: Cafe): string[] {
  return cafe.sensoryData?.[0]?.vibeKeywords || []
}

function getRecommendedFor(cafe: Cafe): string[] {
  return cafe.sensoryData?.[0]?.recommendedFor || []
}

function formatDistance(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)}m`
  return `${km.toFixed(1)}km`
}

function loadMore() {
  if (displayCount.value < filteredCafes.value.length) {
    displayCount.value = Math.min(displayCount.value + PAGE_SIZE, filteredCafes.value.length)
  }
}

function setupObserver() {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) loadMore()
    },
    { rootMargin: '200px' }
  )
  if (sentinel.value) observer.observe(sentinel.value)
}

async function handleSearch() {
  const q = searchQuery.value.trim()
  if (!q) return

  try {
    const res = await axios.get<Cafe[]>(`/api/cafes/search?q=${encodeURIComponent(q)}`)
    const results = res.data
    if (results.length > 0) {
      // Move map to first matching cafe
      const target = results[0]
      if (target.latitude && target.longitude) {
        mapCenter.value = { lat: target.latitude, lng: target.longitude }
      }
    }
  } catch (e) {
    console.error('Search failed:', e)
  }
}

function clearSearch() {
  searchQuery.value = ''
  selectedTag.value = ''
  displayCount.value = PAGE_SIZE
}

function toggleTag(tag: string) {
  selectedTag.value = selectedTag.value === tag ? '' : tag
  displayCount.value = PAGE_SIZE
}

function goToDetail(id: number) {
  router.push({ name: 'cafe-detail', params: { id } })
}

async function onMapCenterChanged(lat: number, lng: number) {
  mapCenter.value = { lat, lng }
  try {
    const res = await axios.get<Cafe[]>(`/api/cafes/nearby?lat=${lat}&lng=${lng}&limit=200`)
    cafes.value = res.data
  } catch (e) {
    console.error('nearby 갱신 실패:', e)
  }
}

function onMapBoundsChanged(swLat: number, swLng: number, neLat: number, neLng: number) {
  mapBounds.value = { swLat, swLng, neLat, neLng }
}

async function loadDefault() {
  loading.value = true
  try {
    // 위치 기반 시도
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          locationAvailable.value = true
          const res = await axios.get<Cafe[]>(`/api/cafes/nearby?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}&limit=200`)
          cafes.value = res.data
          loading.value = false
        },
        async () => {
          // 위치 거부 시 전체 목록
          locationAvailable.value = false
          const res = await axios.get<Cafe[]>('/api/cafes')
          cafes.value = res.data
          loading.value = false
        },
        { timeout: 5000, enableHighAccuracy: false }
      )
    } else {
      const res = await axios.get<Cafe[]>('/api/cafes')
      cafes.value = res.data
      loading.value = false
    }
  } catch (e) {
    console.error('카페 로드 실패:', e)
    loading.value = false
  }
}

onMounted(() => {
  loadDefault()
  // sentinel 관찰 지연 (DOM 렌더 후)
  setTimeout(setupObserver, 500)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.cafe-search-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 40px;
}

/* ── 히어로 검색 ── */
.search-hero {
  text-align: center;
  padding: 48px 0 32px;
}
.hero-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1a1a2e;
  margin-bottom: 8px;
}
.hero-title .accent {
  background: linear-gradient(135deg, #e8985e, #d4764e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-subtitle {
  color: #8892a4;
  font-size: 0.95rem;
  margin-bottom: 28px;
}

/* 검색바 */
.search-container {
  max-width: 560px;
  margin: 0 auto 20px;
}
.search-input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f6f8;
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 4px 16px;
  transition: all 0.3s ease;
}
.search-input-wrapper:focus-within {
  background: #fff;
  border-color: #e8985e;
  box-shadow: 0 4px 20px rgba(232, 152, 94, 0.12);
}
.search-icon {
  width: 20px;
  height: 20px;
  color: #aab0bc;
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 14px 12px;
  font-size: 1rem;
  color: #1a1a2e;
  outline: none;
}
.search-input::placeholder {
  color: #b0b7c3;
}
.search-clear {
  background: none;
  border: none;
  color: #aab0bc;
  cursor: pointer;
  font-size: 1rem;
  padding: 4px 8px;
  border-radius: 50%;
  transition: background 0.2s;
}
.search-clear:hover {
  background: #e8e8e8;
}
.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #e8985e, #d4764e);
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}
.search-btn svg {
  width: 18px;
  height: 18px;
}
.search-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(232, 152, 94, 0.3);
}

/* 빠른 필터 태그 */
.quick-filters {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  max-width: 560px;
  margin: 0 auto;
}
.filter-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border: 1.5px solid #e4e7ec;
  border-radius: 24px;
  background: #fff;
  color: #5a6175;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-tag:hover {
  border-color: #e8985e;
  color: #e8985e;
}
.filter-tag.active {
  background: linear-gradient(135deg, #e8985e, #d4764e);
  border-color: transparent;
  color: #fff;
}
.tag-emoji {
  font-size: 0.9rem;
}

/* ── 결과 섹션 ── */
.results-section {
  margin-top: 8px;
}
.results-header {
  margin-bottom: 16px;
}
.results-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a2e;
}
.results-count {
  color: #e8985e;
  font-weight: 600;
  margin-left: 6px;
}

/* 로딩 */
.loading-state {
  text-align: center;
  padding: 48px 0;
  color: #8892a4;
}
.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e4e7ec;
  border-top-color: #e8985e;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 빈 결과 */
.empty-state {
  text-align: center;
  padding: 48px 0;
  color: #8892a4;
}
.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}
.empty-hint {
  font-size: 0.85rem;
  color: #b0b7c3;
}

/* ── 컴팩트 리스트 아이템 ── */
.cafe-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.cafe-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: #fff;
  border: 1px solid #eef0f4;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.cafe-item:hover {
  border-color: #e8985e;
  box-shadow: 0 4px 16px rgba(232, 152, 94, 0.1);
  transform: translateX(4px);
}

.cafe-thumb-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
}
.cafe-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cafe-info {
  flex: 1;
  min-width: 0;
}
.cafe-info-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.cafe-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cafe-distance {
  font-size: 0.78rem;
  color: #e8985e;
  font-weight: 600;
  white-space: nowrap;
  background: rgba(232, 152, 94, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
}
.cafe-address {
  font-size: 0.8rem;
  color: #8892a4;
  margin: 2px 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cafe-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.meta-badges {
  display: flex;
  gap: 6px;
}
.meta-badge {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  white-space: nowrap;
}
.meta-badge.taste {
  background: #fef3e8;
  color: #d4764e;
}
.meta-badge.noise {
  background: #edf7ed;
  color: #4caf50;
}
.meta-badge.light {
  background: #fff8e1;
  color: #f9a825;
}

.cafe-tags {
  display: flex;
  gap: 4px;
}
.vibe-tag {
  font-size: 0.72rem;
  color: #7c8db5;
  font-weight: 500;
}

.cafe-purposes {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}
.purpose-badge {
  font-size: 0.68rem;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f0f1f5;
  color: #6b7280;
  font-weight: 500;
}

.cafe-arrow {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  color: #cdd1da;
}
.cafe-item:hover .cafe-arrow {
  color: #e8985e;
}

/* 반응형 */
@media (max-width: 480px) {
  .hero-title { font-size: 1.5rem; }
  .quick-filters { gap: 6px; }
  .filter-tag { padding: 6px 10px; font-size: 0.8rem; }
  .cafe-thumb-wrapper { width: 52px; height: 52px; }
}

/* 무한스크롤 */
.sentinel { height: 1px; }
.load-more-area { padding: 16px 0 8px; text-align: center; }
.loading-more { display: flex; justify-content: center; padding: 8px 0; }
.loading-spinner-sm {
  width: 24px; height: 24px;
  border: 2.5px solid #e4e7ec;
  border-top-color: #e8985e;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.all-loaded {
  font-size: 0.82rem;
  color: #b0b7c3;
  padding: 8px 0;
}

/* 크리마 점수 */
.cafe-top-badges { display: flex; gap: 8px; align-items: center; }
.creama-score {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  letter-spacing: 0.2px;
}
.score-high { background: linear-gradient(135deg, #fff3e0, #ffe0b2); color: #e65100; }
.score-mid { background: #eef2f7; color: #5c6b7a; }
.score-low { background: #f5f5f5; color: #9e9e9e; }

/* 지도 섹션 */
.map-section {
  max-width: 700px;
  margin: 0 auto 8px;
  padding: 0 16px;
  text-align: center;
}
.map-toggle-btn {
  display: none;
}
</style>
