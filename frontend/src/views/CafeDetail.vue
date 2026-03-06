<template>
  <div class="cafe-detail-page" v-if="cafe">
    <!-- 뒤로가기 -->
    <button class="back-btn" @click="router.back()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      돌아가기
    </button>

    <!-- 히어로 배너 -->
    <section class="hero-banner">
      <img :src="cafe.mainImageUrl" :alt="cafe.name" class="hero-image" />
      <div class="hero-overlay">
        <h1 class="hero-name">{{ cafe.name }}</h1>
        <p class="hero-address">📍 {{ cafe.address }}</p>
      </div>
    </section>

    <!-- 크리마 점수 -->
    <section class="creama-score-card" v-if="cafe.creamaScore != null">
      <div class="score-circle" :class="detailScoreClass">
        <span class="score-number">{{ cafe.creamaScore.toFixed(1) }}</span>
        <span class="score-label">/ 10</span>
      </div>
      <div class="score-info">
        <h3 class="score-title">Creama Score</h3>
        <p class="score-desc">{{ scoreDescription }}</p>
      </div>
    </section>

    <!-- 기본 정보 카드 -->
    <section class="info-card" v-if="cafe.phone || cafe.operatingHours">
      <div class="info-row" v-if="cafe.phone">
        <span class="info-icon">📞</span>
        <span>{{ cafe.phone }}</span>
      </div>
      <div class="info-row" v-if="cafe.operatingHours">
        <span class="info-icon">🕐</span>
        <span>{{ cafe.operatingHours }}</span>
      </div>
    </section>

    <!-- 감성 키워드 -->
    <section class="section" v-if="vibeKeywords.length > 0">
      <h2 class="section-title">🎨 감성 & 분위기</h2>
      <div class="vibe-tags">
        <span v-for="vibe in vibeKeywords" :key="vibe" class="vibe-chip">
          {{ vibe }}
        </span>
      </div>
    </section>

    <!-- 추천 용도 -->
    <section class="section" v-if="recommendedFor.length > 0">
      <h2 class="section-title">🎯 이런 분에게 추천</h2>
      <div class="purpose-tags">
        <span v-for="purpose in recommendedFor" :key="purpose" class="purpose-chip">
          {{ purpose }}
        </span>
      </div>
    </section>

    <!-- 시설 정보 -->
    <section class="section" v-if="sensory">
      <h2 class="section-title">🪑 시설 정보</h2>
      <div class="facilities-grid">
        <div :class="['facility-item', { active: sensory.hasWifi }]">
          <span class="facility-icon">📶</span>
          <span class="facility-label">와이파이</span>
        </div>
        <div :class="['facility-item', { active: sensory.hasConcent }]">
          <span class="facility-icon">🔌</span>
          <span class="facility-label">콘센트</span>
        </div>
        <div :class="['facility-item', { active: sensory.hasParking }]">
          <span class="facility-icon">🅿️</span>
          <span class="facility-label">주차</span>
        </div>
        <div class="facility-item active" v-if="sensory.musicGenre">
          <span class="facility-icon">🎵</span>
          <span class="facility-label">{{ sensory.musicGenre }}</span>
        </div>
      </div>
      
      <!-- 좌석 유형 -->
      <div class="seat-types" v-if="seatTypes.length > 0">
        <span class="seat-label">좌석:</span>
        <span v-for="seat in seatTypes" :key="seat" class="seat-chip">{{ seat }}</span>
      </div>
    </section>

    <!-- 맛 프로필 레이더 차트 -->
    <section class="section" v-if="sensory">
      <h2 class="section-title">☕ 맛 프로필</h2>
      <div class="chart-container">
        <RadarChart :sensory-data="sensory" />
      </div>
    </section>

    <!-- 분위기 메트릭 -->
    <section class="section" v-if="sensory">
      <h2 class="section-title">🌡️ 분위기 지표</h2>
      <div class="vibe-meters">
        <div class="meter-item">
          <div class="meter-header">
            <span class="meter-label">🔇 소음</span>
            <span class="meter-value">{{ sensory.noiseLevel }}</span>
          </div>
          <div class="meter-bar">
            <div class="meter-fill noise" :style="{ width: sensory.noiseLevel + '%' }"></div>
          </div>
          <div class="meter-desc">{{ noiseDesc }}</div>
        </div>
        <div class="meter-item">
          <div class="meter-header">
            <span class="meter-label">💡 조명</span>
            <span class="meter-value">{{ sensory.lighting }}</span>
          </div>
          <div class="meter-bar">
            <div class="meter-fill light" :style="{ width: sensory.lighting + '%' }"></div>
          </div>
          <div class="meter-desc">{{ lightDesc }}</div>
        </div>
        <div class="meter-item">
          <div class="meter-header">
            <span class="meter-label">🛋️ 편안함</span>
            <span class="meter-value">{{ sensory.comfort }}</span>
          </div>
          <div class="meter-bar">
            <div class="meter-fill comfort" :style="{ width: sensory.comfort + '%' }"></div>
          </div>
          <div class="meter-desc">{{ comfortDesc }}</div>
        </div>
        <div class="meter-item" v-if="sensory.crowdedness !== null">
          <div class="meter-header">
            <span class="meter-label">👥 혼잡도</span>
            <span class="meter-value">{{ sensory.crowdedness }}</span>
          </div>
          <div class="meter-bar">
            <div class="meter-fill crowd" :style="{ width: sensory.crowdedness + '%' }"></div>
          </div>
          <div class="meter-desc">{{ crowdDesc }}</div>
        </div>
      </div>
    </section>

    <!-- 분위기 사진 갤러리 -->
    <section class="section" v-if="cafe.imageUrls && cafe.imageUrls.length > 0">
      <h2 class="section-title">📸 분위기 사진</h2>
      <div class="gallery">
        <div v-for="(url, idx) in cafe.imageUrls" :key="idx" class="gallery-item">
          <img :src="url" :alt="`${cafe.name} 사진 ${idx + 1}`" loading="lazy" />
        </div>
      </div>
    </section>

    <!-- 키워드 태그 -->
    <section class="section" v-if="keywords.length > 0">
      <h2 class="section-title">🏷️ 키워드</h2>
      <div class="keyword-tags">
        <span v-for="kw in keywords" :key="kw" class="keyword-chip">
          #{{ kw }}
        </span>
      </div>
    </section>

    <!-- 한줄 리뷰 작성 -->
    <section class="section">
      <h2 class="section-title">✍️ 한줄 리뷰</h2>
      <div class="review-form">
        <input
          v-model="reviewNickname"
          type="text"
          class="review-nickname"
          placeholder="닉네임"
          maxlength="20"
        />
        <textarea
          v-model="reviewContent"
          class="review-textarea"
          placeholder="이 카페에 대해 한줄로 적어주세요..."
          maxlength="200"
          rows="2"
        ></textarea>
        <div class="review-actions">
          <label class="photo-upload-btn">
            📷 사진 첨부
            <input type="file" accept="image/*" @change="handleImageSelect" hidden />
          </label>
          <span v-if="reviewImageFile" class="selected-file">
            {{ reviewImageFile.name }}
            <button class="remove-file" @click="removeImage">✕</button>
          </span>
          <button
            class="submit-review-btn"
            :disabled="!reviewContent.trim() || !reviewNickname.trim() || submitting"
            @click="submitReview"
          >
            {{ submitting ? '등록 중...' : '등록' }}
          </button>
        </div>
        <div v-if="reviewImagePreview" class="image-preview">
          <img :src="reviewImagePreview" alt="미리보기" />
        </div>
      </div>

      <!-- 리뷰 목록 -->
      <div class="reviews-list" v-if="reviews.length > 0">
        <div v-for="review in reviews" :key="review.id" class="review-item">
          <div class="review-header">
            <span class="review-nickname">{{ review.nickname }}</span>
            <span class="review-date">{{ review.createdAt }}</span>
          </div>
          <p class="review-content">{{ review.content }}</p>
          <img
            v-if="review.imageUrl"
            :src="review.imageUrl"
            :alt="review.nickname + '의 사진'"
            class="review-image"
            loading="lazy"
          />
        </div>
      </div>
      <p v-else class="no-reviews">아직 리뷰가 없어요. 첫 번째 리뷰를 남겨보세요!</p>
    </section>
  </div>

  <!-- 로딩 -->
  <div v-else class="loading-page">
    <div class="loading-spinner"></div>
    <p>카페 정보를 불러오고 있어요...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import RadarChart from '../components/RadarChart.vue'

const route = useRoute()
const router = useRouter()

interface SensoryData {
  acidity: number; body: number; sweetness: number; bitterness: number; aroma: number
  noiseLevel: number; lighting: number; comfort: number
  musicGenre: string; crowdedness: number
  hasConcent: boolean; hasWifi: boolean; hasParking: boolean
  seatTypes: string[]; vibeKeywords: string[]; recommendedFor: string[]; keywords: string[]
}

interface Cafe {
  id: number; name: string; address: string
  latitude: number; longitude: number
  mainImageUrl: string; phone: string; operatingHours: string
  imageUrls: string[]; sensoryData: SensoryData[]
  creamaScore?: number
}

interface ReviewData {
  id: number
  cafeId: number
  nickname: string
  content: string
  imageUrl: string | null
  createdAt: string
}

const cafe = ref<Cafe | null>(null)
const reviews = ref<ReviewData[]>([])
const reviewNickname = ref('')
const reviewContent = ref('')
const reviewImageFile = ref<File | null>(null)
const reviewImagePreview = ref<string | null>(null)
const submitting = ref(false)

const sensory = computed(() => cafe.value?.sensoryData?.[0] || null)
const vibeKeywords = computed(() => sensory.value?.vibeKeywords || [])
const recommendedFor = computed(() => sensory.value?.recommendedFor || [])
const seatTypes = computed(() => sensory.value?.seatTypes || [])
const keywords = computed(() => sensory.value?.keywords || [])

const detailScoreClass = computed(() => {
  const s = cafe.value?.creamaScore ?? 0
  if (s >= 7.5) return 'detail-score-high'
  if (s >= 5.0) return 'detail-score-mid'
  return 'detail-score-low'
})

const scoreDescription = computed(() => {
  const s = cafe.value?.creamaScore ?? 0
  if (s >= 8.5) return '최고의 카페 경험이에요!'
  if (s >= 7.0) return '꼭 방문할 가치가 있어요'
  if (s >= 5.5) return '괜찮은 카페예요'
  if (s >= 3.5) return '보통 수준이에요'
  return '아직 정보가 부족해요'
})

const noiseDesc = computed(() => {
  const v = sensory.value?.noiseLevel ?? 50
  if (v <= 20) return '도서관처럼 조용해요'
  if (v <= 40) return '대화하기 적당한 정도'
  if (v <= 60) return '활기찬 분위기'
  return '시끌벅적한 편이에요'
})
const lightDesc = computed(() => {
  const v = sensory.value?.lighting ?? 50
  if (v <= 25) return '어두운 무드 조명'
  if (v <= 50) return '은은한 조명'
  if (v <= 75) return '자연광이 충분해요'
  return '밝고 환한 공간'
})
const comfortDesc = computed(() => {
  const v = sensory.value?.comfort ?? 50
  if (v <= 30) return '단단한 의자'
  if (v <= 60) return '적당히 편안해요'
  return '푹신한 소파석이 있어요'
})
const crowdDesc = computed(() => {
  const v = sensory.value?.crowdedness ?? 50
  if (v <= 25) return '한산한 편이에요'
  if (v <= 50) return '적당한 사람들'
  if (v <= 75) return '사람이 좀 있어요'
  return '항상 붐비는 인기 카페'
})

function handleImageSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    reviewImageFile.value = file
    const reader = new FileReader()
    reader.onload = (ev) => { reviewImagePreview.value = ev.target?.result as string }
    reader.readAsDataURL(file)
  }
}

function removeImage() {
  reviewImageFile.value = null
  reviewImagePreview.value = null
}

async function submitReview() {
  if (!cafe.value || !reviewContent.value.trim() || !reviewNickname.value.trim()) return
  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('nickname', reviewNickname.value.trim())
    formData.append('content', reviewContent.value.trim())
    if (reviewImageFile.value) {
      formData.append('image', reviewImageFile.value)
    }
    const res = await axios.post<ReviewData>(`/api/cafes/${cafe.value.id}/reviews`, formData)
    reviews.value.unshift(res.data)
    reviewNickname.value = ''
    reviewContent.value = ''
    removeImage()
  } catch (e) {
    console.error('리뷰 등록 실패:', e)
  } finally {
    submitting.value = false
  }
}

async function loadReviews(cafeId: number) {
  try {
    const res = await axios.get<ReviewData[]>(`/api/cafes/${cafeId}/reviews`)
    reviews.value = res.data
  } catch (e) {
    console.error('리뷰 로드 실패:', e)
  }
}

onMounted(async () => {
  try {
    const cafeId = route.params.id as string
    const res = await axios.get<Cafe>(`/api/cafes/${cafeId}`)
    cafe.value = res.data
    loadReviews(Number(cafeId))
  } catch (e) {
    console.error('카페 정보 로드 실패:', e)
  }
})
</script>

<style scoped>
.cafe-detail-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 0 16px 40px;
}

/* 뒤로가기 */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1.5px solid #e4e7ec;
  border-radius: 10px;
  background: #fff;
  color: #5a6175;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  margin: 16px 0;
  transition: all 0.2s;
}
.back-btn:hover {
  border-color: #e8985e;
  color: #e8985e;
}

/* 히어로 배너 */
.hero-banner {
  position: relative;
  width: 100%;
  height: 280px;
  border-radius: 18px;
  overflow: hidden;
  margin-bottom: 20px;
}
.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px 24px 20px;
  background: linear-gradient(transparent, rgba(0,0,0,0.65));
}
.hero-name {
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 4px;
}
.hero-address {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.85);
}

/* 기본 정보 카드 */
.info-card {
  background: #f8f9fb;
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #3a3f51;
}
.info-icon {
  font-size: 1rem;
}

/* 섹션 */
.section {
  margin-bottom: 28px;
}
.section-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 14px;
}

/* 감성 키워드 */
.vibe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.vibe-chip {
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(232,152,94,0.1), rgba(212,118,78,0.08));
  border: 1px solid rgba(232,152,94,0.2);
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #d4764e;
}

/* 추천 용도 */
.purpose-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.purpose-chip {
  padding: 8px 16px;
  background: #eef4ff;
  border: 1px solid #d0e2ff;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #3b7ddd;
}

/* 시설 정보 */
.facilities-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}
.facility-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  border-radius: 12px;
  background: #f5f5f5;
  opacity: 0.4;
  transition: all 0.2s;
}
.facility-item.active {
  background: #f0f9f0;
  opacity: 1;
}
.facility-icon {
  font-size: 1.3rem;
}
.facility-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #3a3f51;
}

.seat-types {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.seat-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #6b7280;
}
.seat-chip {
  font-size: 0.78rem;
  padding: 4px 10px;
  background: #f0f1f5;
  border-radius: 8px;
  color: #5a6175;
}

/* 레이더 차트 */
.chart-container {
  background: #fff;
  border: 1px solid #eef0f4;
  border-radius: 16px;
  padding: 20px;
  max-width: 400px;
  margin: 0 auto;
}

/* 분위기 메트릭 바 */
.vibe-meters {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.meter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.meter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.meter-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #3a3f51;
}
.meter-value {
  font-size: 0.78rem;
  font-weight: 700;
  color: #8892a4;
}
.meter-bar {
  height: 8px;
  background: #eef0f4;
  border-radius: 4px;
  overflow: hidden;
}
.meter-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}
.meter-fill.noise { background: linear-gradient(90deg, #4caf50, #ff9800); }
.meter-fill.light { background: linear-gradient(90deg, #5c6bc0, #ffeb3b); }
.meter-fill.comfort { background: linear-gradient(90deg, #78909c, #e91e63); }
.meter-fill.crowd { background: linear-gradient(90deg, #26a69a, #ef5350); }
.meter-desc {
  font-size: 0.75rem;
  color: #8892a4;
}

/* 사진 갤러리 */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
}
.gallery-item img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: 12px;
}

/* 키워드 태그 */
.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.keyword-chip {
  font-size: 0.85rem;
  color: #7c8db5;
  font-weight: 500;
}

/* 로딩 페이지 */
.loading-page {
  text-align: center;
  padding: 80px 0;
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

/* 리뷰 폼 */
.review-form {
  background: #f8f9fb;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 20px;
}
.review-form .review-nickname {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid #e4e7ec;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-bottom: 8px;
  outline: none;
  background: #fff;
  box-sizing: border-box;
}
.review-form .review-nickname:focus {
  border-color: #e8985e;
}
.review-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid #e4e7ec;
  border-radius: 10px;
  font-size: 0.9rem;
  resize: none;
  outline: none;
  font-family: inherit;
  background: #fff;
  box-sizing: border-box;
}
.review-textarea:focus {
  border-color: #e8985e;
}
.review-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.photo-upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border: 1.5px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  color: #5a6175;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}
.photo-upload-btn:hover {
  border-color: #e8985e;
  color: #e8985e;
}
.selected-file {
  font-size: 0.78rem;
  color: #8892a4;
  display: flex;
  align-items: center;
  gap: 4px;
}
.remove-file {
  background: none;
  border: none;
  color: #ef5350;
  cursor: pointer;
  font-size: 0.82rem;
}
.submit-review-btn {
  margin-left: auto;
  padding: 8px 20px;
  background: linear-gradient(135deg, #e8985e, #d4764e);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.submit-review-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.submit-review-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(232,152,94,0.3);
}
.image-preview {
  margin-top: 10px;
}
.image-preview img {
  max-width: 200px;
  max-height: 150px;
  border-radius: 10px;
  object-fit: cover;
}

/* 리뷰 목록 */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.review-item {
  background: #fff;
  border: 1px solid #eef0f4;
  border-radius: 12px;
  padding: 14px 16px;
}
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.review-item .review-nickname {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1a1a2e;
}
.review-date {
  font-size: 0.72rem;
  color: #aab0bc;
}
.review-content {
  font-size: 0.9rem;
  color: #3a3f51;
  line-height: 1.5;
  margin: 0;
}
.review-image {
  margin-top: 10px;
  max-width: 100%;
  max-height: 200px;
  border-radius: 10px;
  object-fit: cover;
}
.no-reviews {
  text-align: center;
  color: #aab0bc;
  font-size: 0.85rem;
  padding: 20px 0;
}

/* 크리마 점수 카드 */
.creama-score-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  margin-bottom: 12px;
}
.score-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  flex-shrink: 0;
}
.detail-score-high {
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
  border: 2px solid #ffb74d;
}
.detail-score-mid {
  background: #eef2f7;
  border: 2px solid #c5cdd9;
}
.detail-score-low {
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
}
.score-number {
  font-size: 1.3rem;
  font-weight: 800;
  line-height: 1;
  color: #333;
}
.score-label {
  font-size: 0.65rem;
  color: #999;
}
.score-info { flex: 1; }
.score-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #e8985e;
  margin: 0 0 2px 0;
}
.score-desc {
  font-size: 0.82rem;
  color: #7c8db5;
  margin: 0;
}

@media (max-width: 480px) {
  .hero-banner { height: 200px; }
  .hero-name { font-size: 1.3rem; }
  .facilities-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
