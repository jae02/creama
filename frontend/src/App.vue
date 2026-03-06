<template>
  <div class="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
    <!-- 헤더 -->
    <header class="bg-white shadow-sm border-b border-amber-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <router-link to="/" class="block w-fit">
          <h1 class="text-4xl font-bold text-amber-900 hover:text-amber-700 transition-colors duration-200">
            ☕️ Creama
          </h1>
        </router-link>
        <p class="text-amber-700 mt-2">Discover cafes by taste &amp; vibe</p>
      </div>
    </header>

    <!-- 페이지 콘텐츠 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
// App.vue는 레이아웃 껍데기만 담당
// 실제 페이지 내용은 views/CafeList.vue, views/CafeDetail.vue에서 처리
</script>
