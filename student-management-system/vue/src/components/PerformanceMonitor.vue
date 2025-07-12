<template>
  <div v-if="showMonitor" class="performance-monitor">
    <div class="monitor-item">
      <span>数据量:</span>
      <span>{{ dataCount }}</span>
    </div>
    <div class="monitor-item">
      <span>渲染时间:</span>
      <span>{{ renderTime }}ms</span>
    </div>
    <div class="monitor-item">
      <span>内存使用:</span>
      <span>{{ memoryUsage }}MB</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  dataCount: {
    type: Number,
    default: 0
  },
  showMonitor: {
    type: Boolean,
    default: false
  }
})

const renderTime = ref(0)
const memoryUsage = ref(0)

let performanceObserver = null

onMounted(() => {
  if (props.showMonitor) {
    startMonitoring()
  }
})

onUnmounted(() => {
  if (performanceObserver) {
    performanceObserver.disconnect()
  }
})

const startMonitoring = () => {
  // 监控渲染性能
  if ('PerformanceObserver' in window) {
    performanceObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'measure') {
          renderTime.value = Math.round(entry.duration)
        }
      }
    })
    
    performanceObserver.observe({ entryTypes: ['measure'] })
  }
  
  // 监控内存使用
  if ('memory' in performance) {
    const updateMemory = () => {
      memoryUsage.value = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)
      setTimeout(updateMemory, 2000)
    }
    updateMemory()
  }
}
</script>

<style scoped>
.performance-monitor {
  position: fixed;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  z-index: 9999;
}

.monitor-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  min-width: 120px;
}
</style> 