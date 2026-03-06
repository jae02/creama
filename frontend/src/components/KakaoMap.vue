<template>
  <div class="kakao-map-wrapper">
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'

declare global {
  interface Window {
    kakao: any
  }
}

interface CafeMarker {
  id: number
  name: string
  latitude: number
  longitude: number
  creamaScore?: number
  address?: string
}

const props = defineProps<{
  cafes: CafeMarker[]
  centerLat?: number
  centerLng?: number
}>()

const emit = defineEmits<{
  (e: 'center-changed', lat: number, lng: number): void
  (e: 'bounds-changed', swLat: number, swLng: number, neLat: number, neLng: number): void
}>()

const router = useRouter()
const mapContainer = ref<HTMLElement | null>(null)
let map: any = null
let markers: any[] = []
let infoWindow: any = null
let moveTimeout: ReturnType<typeof setTimeout> | null = null

function getMarkerColor(score?: number): string {
  if (!score || score === 0) return '#aab0bc'
  if (score >= 7.5) return '#e65100'
  if (score >= 5.0) return '#5c6b7a'
  return '#9e9e9e'
}

function createMarkerImage(score?: number) {
  const kakao = window.kakao
  const color = getMarkerColor(score)
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="38" viewBox="0 0 28 38">
    <path d="M14 0C6.3 0 0 6.3 0 14c0 10.5 14 24 14 24s14-13.5 14-24C28 6.3 21.7 0 14 0z" fill="${color}"/>
    <circle cx="14" cy="14" r="6" fill="white"/>
  </svg>`
  const blob = new Blob([svg], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  return new kakao.maps.MarkerImage(
    url,
    new kakao.maps.Size(28, 38),
    { offset: new kakao.maps.Point(14, 38) }
  )
}

function clearMarkers() {
  markers.forEach(m => m.setMap(null))
  markers = []
}

function updateMarkers() {
  if (!map) return
  const kakao = window.kakao
  clearMarkers()

  if (infoWindow) infoWindow.close()

  props.cafes.forEach(cafe => {
    if (!cafe.latitude || !cafe.longitude) return

    const position = new kakao.maps.LatLng(cafe.latitude, cafe.longitude)
    const marker = new kakao.maps.Marker({
      position,
      map,
      image: createMarkerImage(cafe.creamaScore),
      title: cafe.name
    })

    const scoreText = cafe.creamaScore != null ? `<span style="color:#e65100;font-weight:700">★ ${cafe.creamaScore.toFixed(1)}</span>` : ''
    const content = `
      <div style="padding:8px 12px;min-width:160px;font-size:13px;line-height:1.5;border-radius:8px">
        <strong style="font-size:14px">${cafe.name}</strong> ${scoreText}<br/>
        <span style="color:#888;font-size:12px">${cafe.address || ''}</span><br/>
        <a href="javascript:void(0)" data-cafe-id="${cafe.id}"
          style="color:#e8985e;font-size:12px;font-weight:600;text-decoration:none">
          상세 보기 →
        </a>
      </div>`

    kakao.maps.event.addListener(marker, 'click', () => {
      if (infoWindow) infoWindow.close()
      infoWindow = new kakao.maps.InfoWindow({ content, removable: true })
      infoWindow.open(map, marker)

      // 인포윈도우 내 링크 클릭 감지
      setTimeout(() => {
        const link = document.querySelector(`a[data-cafe-id="${cafe.id}"]`)
        if (link) {
          link.addEventListener('click', () => {
            router.push({ name: 'cafe-detail', params: { id: cafe.id } })
          })
        }
      }, 100)
    })

    markers.push(marker)
  })
}

function initMap() {
  const kakao = window.kakao
  if (!kakao?.maps || !mapContainer.value) return

  const lat = props.centerLat || 37.5488
  const lng = props.centerLng || 127.0877

  const options = {
    center: new kakao.maps.LatLng(lat, lng),
    level: 5
  }

  map = new kakao.maps.Map(mapContainer.value, options)

  // 지도 이동 완료 시 중심 좌표 + bounds emit (디바운스)
  kakao.maps.event.addListener(map, 'idle', () => {
    if (moveTimeout) clearTimeout(moveTimeout)
    moveTimeout = setTimeout(() => {
      const center = map.getCenter()
      emit('center-changed', center.getLat(), center.getLng())
      const bounds = map.getBounds()
      const sw = bounds.getSouthWest()
      const ne = bounds.getNorthEast()
      emit('bounds-changed', sw.getLat(), sw.getLng(), ne.getLat(), ne.getLng())
    }, 500)
  })

  updateMarkers()
}

watch(() => props.cafes, () => {
  nextTick(() => updateMarkers())
}, { deep: true })

watch([() => props.centerLat, () => props.centerLng], ([lat, lng]) => {
  if (map && lat && lng) {
    const kakao = window.kakao
    map.setCenter(new kakao.maps.LatLng(lat, lng))
  }
})

function loadKakaoSDK(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      resolve()
      return
    }
    const existing = document.getElementById('kakao-sdk')
    if (existing) {
      // 이미 삽입됐지만 아직 로드 중
      const check = setInterval(() => {
        if (window.kakao?.maps) { clearInterval(check); resolve() }
      }, 200)
      setTimeout(() => { clearInterval(check); reject(new Error('Kakao SDK timeout')) }, 10000)
      return
    }
    const script = document.createElement('script')
    script.id = 'kakao-sdk'
    script.type = 'text/javascript'
    script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=a4f0196a6c25aa2fbda2009e9fc7531f&autoload=false'
    script.onload = () => {
      window.kakao.maps.load(() => resolve())
    }
    script.onerror = () => reject(new Error('Kakao SDK load error'))
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  try {
    await loadKakaoSDK()
    initMap()
  } catch (e) {
    console.error('카카오 지도 SDK 로드 실패:', e)
  }
})
</script>

<style scoped>
.kakao-map-wrapper {
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 16px;
}
.map-container {
  width: 100%;
  height: 360px;
}
</style>
