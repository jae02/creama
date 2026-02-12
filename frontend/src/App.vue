<template>
  <div class="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-amber-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 class="text-4xl font-bold text-amber-900">
          ☕️ Creama
        </h1>
        <p class="text-amber-700 mt-2">Discover cafes by taste & vibe</p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-900"></div>
        <p class="mt-4 text-amber-700">Loading cafes...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- Cafe Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div
          v-for="cafe in cafes"
          :key="cafe.id"
          class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-shadow duration-300"
        >
          <!-- Cafe Image -->
          <div class="h-48 bg-gradient-to-br from-amber-400 to-orange-500 relative overflow-hidden">
            <img
              v-if="cafe.mainImageUrl"
              :src="cafe.mainImageUrl"
              :alt="cafe.name"
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-black bg-opacity-20"></div>
            <div class="absolute bottom-4 left-4 right-4">
              <h2 class="text-2xl font-bold text-white drop-shadow-lg">{{ cafe.name }}</h2>
            </div>
          </div>

          <!-- Cafe Info -->
          <div class="p-6">
            <p class="text-sm text-gray-600 mb-4">{{ cafe.address }}</p>

            <!-- Sensory Data -->
            <div v-if="cafe.sensoryData && cafe.sensoryData.length > 0">
              <div v-for="sensory in cafe.sensoryData" :key="sensory.id">
                <!-- Radar Chart -->
                <div class="mb-4">
                  <h3 class="text-sm font-semibold text-amber-900 mb-3">Taste Profile</h3>
                  <RadarChart :sensory-data="sensory" />
                </div>

                <!-- Vibe Metrics -->
                <div class="space-y-2">
                  <h3 class="text-sm font-semibold text-amber-900 mb-2">Vibe Metrics</h3>
                  
                  <div>
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                      <span>🔊 Noise</span>
                      <span>{{ sensory.noiseLevel }}/100</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-blue-500 h-2 rounded-full"
                        :style="{ width: sensory.noiseLevel + '%' }"
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                      <span>💡 Lighting</span>
                      <span>{{ sensory.lighting }}/100</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-yellow-500 h-2 rounded-full"
                        :style="{ width: sensory.lighting + '%' }"
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                      <span>🛋️ Comfort</span>
                      <span>{{ sensory.comfort }}/100</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-green-500 h-2 rounded-full"
                        :style="{ width: sensory.comfort + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>

                <!-- Keywords -->
                <div v-if="sensory.keywords && sensory.keywords.length > 0" class="mt-4">
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="keyword in sensory.keywords"
                      :key="keyword"
                      class="px-3 py-1 bg-amber-100 text-amber-800 text-xs rounded-full font-medium"
                    >
                      {{ keyword }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import RadarChart from './components/RadarChart.vue'

interface SensoryData {
  id: number
  acidity: number
  body: number
  sweetness: number
  bitterness: number
  aroma: number
  noiseLevel: number
  lighting: number
  comfort: number
  keywords: string[]
}

interface Cafe {
  id: number
  name: string
  address: string
  latitude: number
  longitude: number
  mainImageUrl: string
  sensoryData: SensoryData[]
}

const cafes = ref<Cafe[]>([])
const loading = ref(true)
const error = ref('')

const fetchCafes = async () => {
  try {
    const response = await axios.get<Cafe[]>('/api/cafes')
    cafes.value = response.data
  } catch (err) {
    error.value = 'Failed to load cafes. Make sure the backend server is running.'
    console.error('Error fetching cafes:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCafes()
})
</script>
