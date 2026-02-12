<template>
  <div class="radar-chart-container">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import { Radar } from 'vue-chartjs'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

interface SensoryData {
  acidity: number
  body: number
  sweetness: number
  bitterness: number
  aroma: number
}

const props = defineProps<{
  sensoryData: SensoryData
}>()

const chartData = computed(() => ({
  labels: ['Acidity (산미)', 'Body (바디감)', 'Sweetness (단맛)', 'Bitterness (쓴맛)', 'Aroma (향)'],
  datasets: [
    {
      label: 'Taste Profile',
      data: [
        props.sensoryData.acidity,
        props.sensoryData.body,
        props.sensoryData.sweetness,
        props.sensoryData.bitterness,
        props.sensoryData.aroma
      ],
      backgroundColor: 'rgba(217, 119, 6, 0.2)',
      borderColor: 'rgb(217, 119, 6)',
      borderWidth: 2,
      pointBackgroundColor: 'rgb(217, 119, 6)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgb(217, 119, 6)'
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  scales: {
    r: {
      beginAtZero: true,
      max: 5,
      ticks: {
        stepSize: 1,
        font: {
          size: 10
        }
      },
      pointLabels: {
        font: {
          size: 11,
          weight: '600'
        }
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function (context: any) {
          return context.parsed.r.toFixed(1) + ' / 5.0'
        }
      }
    }
  }
}
</script>

<style scoped>
.radar-chart-container {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
